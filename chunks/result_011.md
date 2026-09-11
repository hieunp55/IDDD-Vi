- AJ:    'Anh có muốn đổi chút thông tin lấy một ly đồ uống không?'

LB:    'Xin lỗi nhé, J. Ở đây chúng tôi chỉ nhận cache thôi.'

> 💡 **Giải thích thêm:** Đây là một màn chơi chữ kinh điển trong giới công nghệ. Từ "cache" (bộ nhớ đệm) trong tiếng Anh có phát âm đồng âm với "cash" (tiền mặt) (/kæʃ/). Câu thoại vừa mang nghĩa hài hước đời thường (quán bar không nhận thông tin mà chỉ nhận tiền mặt), vừa ám chỉ về mặt kỹ thuật: hệ thống Data Fabric đang đề cập chỉ chấp nhận và thao tác trực tiếp trên bộ nhớ đệm (cache).
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000160_b25b49625e45e2b7d14d2a32881bb7415c4b6a2d50e4cd403896c0b6080872b5.png)

Một ưu điểm lớn của Data Fabric (hạ tầng dữ liệu phân tán trên bộ nhớ) là khả năng hỗ trợ các domain model (mô hình miền nghiệp vụ) một cách tự nhiên, gần như xóa bỏ hoàn toàn hiện tượng impedance mismatch (sự bất tương thích trở kháng giữa mô hình đối tượng và mô hình lưu trữ dữ liệu quan hệ). Trên thực tế, các distributed cache (bộ nhớ đệm phân tán) của Data Fabric dễ dàng đáp ứng việc duy trì trạng thái bền vững (persistence) cho các đối tượng miền nói chung, và đóng vai trò như các Aggregate Store (kho lưu trữ khối kết tập) nói riêng. 13 Nói một cách đơn giản, một Aggregate (khối kết tập — tập hợp các thực thể và đối tượng giá trị ràng buộc thành một khối nhất quán) được lưu trữ trong cache dạng map của Fabric 14 chính là phần giá trị (value) trong một cặp key-value. Khóa (key) được tạo từ định danh duy nhất toàn cục của Aggregate, còn bản thân trạng thái của Aggregate được tuần tự hóa (serialized) thành biểu diễn nhị phân hoặc chuỗi văn bản để đóng vai trò làm giá trị:

```java
String key = product.productId().id();
byte[] value = Serializer.serialize(product);

// region (đối với GemFire) hoặc cache (đối với Coherence)
region.put(key, value);

```

Do đó, việc sử dụng một Data Fabric với các tính năng gắn liền mật thiết với các khía cạnh kỹ thuật của một domain model mang lại một hệ quả tích cực: khả năng rút ngắn đáng kể chu kỳ phát triển phần mềm. 15

Các ví dụ trong phần này sẽ minh họa cách một Data Fabric có thể lưu trữ một domain model trong cache và kích hoạt các chức năng của hệ thống ở quy mô phân tán. Qua đó, chúng ta sẽ cùng khám phá các phương thức hỗ trợ mẫu kiến trúc CQRS (Command Query Responsibility Segregation — phân tách trách nhiệm giữa lệnh ghi và truy vấn) và Event-Driven Architecture (kiến trúc hướng sự kiện) thông qua các Long-Running Process (tiến trình nghiệp vụ chạy dài hạn).

## Sao chép dữ liệu (Data Replication)

Khi nghĩ về một in-memory data cache (bộ nhớ đệm dữ liệu trong bộ nhớ), chúng ta có thể ngay lập tức nghĩ tới nguy cơ hiện hữu: mất toàn bộ hoặc một phần trạng thái của hệ thống nếu cache gặp sự cố theo cách nào đó. Đây quả thực là một mối lo ngại có thật, nhưng hoàn toàn không đáng ngại khi tính năng dự phòng (redundancy) đã được tích hợp sẵn bên trong Fabric.

13. Gần đây Martin Fowler đã tích cực quảng bá thuật ngữ Aggregate Store, dù khái niệm này thực tế đã tồn tại từ trước đó một thời gian.
14. Trong GemFire, khái niệm này được gọi là một region, nhưng bản chất hoàn toàn tương đồng với khái niệm mà Coherence gọi là cache. Tôi dùng từ cache xuyên suốt để đảm bảo tính nhất quán.
15. Một số kho lưu trữ NoSQL cũng hoạt động tự nhiên như các 'Aggregate Store', giúp đơn giản hóa các khía cạnh kỹ thuật khi triển khai DDD.

Hãy xem xét bộ nhớ đệm do Fabric cung cấp khi áp dụng chiến lược cache-per-Aggregate (mỗi Aggregate một vùng cache riêng). Trong trường hợp đó, Repository (kho lưu trữ đối tượng miền) của một loại Aggregate nhất định sẽ được hỗ trợ bởi một vùng cache chuyên dụng. Một vùng cache chỉ hoạt động trên một node (nút máy chủ) đơn lẻ sẽ rất dễ bị tổn thương trước các sự cố điểm chết duy nhất (single point of failure). Tuy nhiên, một Fabric cung cấp các vùng cache đa node có cơ chế replication (sao chép/nhân bản dữ liệu) sẽ vô cùng tin cậy. Bạn có thể lựa chọn mức độ dự phòng dựa trên xác suất số lượng node có thể gặp sự cố tại bất kỳ thời điểm nào — rủi ro này sẽ trở nên rất hẹp khi số node tham gia càng tăng. Bạn cũng có toàn quyền đánh đổi giữa mức độ dự phòng và hiệu năng, bởi hiển nhiên hiệu năng có thể bị ảnh hưởng bởi số lượng node cần nhân bản trước khi một Aggregate được xác nhận ghi hoàn tất (fully committed).

Dưới đây là một ví dụ về cách thức hoạt động của cơ chế dự phòng cache (hoặc region, tùy thuộc vào Fabric cụ thể). Một node sẽ đóng vai trò là cache/region chính (primary), và bất kỳ số lượng node nào khác sẽ đóng vai trò phụ (secondary). Nếu kho lưu trữ chính gặp sự cố, một tiến trình fail-over (chuyển đổi dự phòng khi gặp sự cố) sẽ diễn ra và một trong các node phụ sẽ được nâng cấp thành node chính mới. Khi node chính cũ phục hồi, toàn bộ dữ liệu lưu trên node chính mới sẽ được sao chép ngược lại sang node vừa phục hồi và node này sẽ trở thành một node phụ.

Một lợi thế bổ sung của các node fail-over là chúng đảm bảo cơ chế chuyển phát bảo đảm (guaranteed delivery) cho các sự kiện được phát ra từ Fabric. Nhờ đó, các cập nhật trên Aggregate và bất kỳ sự kiện nào của Fabric được xuất bản do kết quả của những cập nhật đó sẽ không bao giờ bị thất lạc. Rõ ràng, tính năng dự phòng và sao chép cache là những yếu tố thiết yếu để lưu trữ các đối tượng domain model mang tính sống còn đối với nghiệp vụ.

## Hạ tầng hướng sự kiện và Domain Event (Event-Driven Fabrics and Domain Events)

Một tính năng cốt lõi của Fabric là hỗ trợ phong cách hướng sự kiện (Event-Driven style) với cơ chế chuyển phát bảo đảm. Phần lớn các Fabric đều tích hợp sẵn cơ chế sự kiện mang tính kỹ thuật, tức là việc tự động thông báo các sự kiện liên quan đến những biến động ở cấp độ cache và cấp độ bản ghi (entry-level). Chúng ta không nên nhầm lẫn những sự kiện này với Domain Event (sự kiện miền nghiệp vụ). Chẳng hạn, sự kiện ở cấp độ cache sẽ thông báo về các hiện tượng như khởi tạo lại cache, trong khi sự kiện ở cấp độ bản ghi sẽ thông báo về việc tạo mới hoặc cập nhật một bản ghi dữ liệu.

Dẫu vậy, với một Fabric hỗ trợ kiến trúc mở, chắc chắn phải có cách để hỗ trợ xuất bản các Domain Event trực tiếp từ chính Aggregate. Các Domain Event của bạn có thể sẽ phải kế thừa một kiểu sự kiện cụ thể của framework, chẳng hạn như `EntryEvent` (ví dụ trong GemFire), nhưng đó chỉ là một cái giá rất nhỏ so với sức mạnh mà chúng đem lại.

Vậy trên thực tế, bạn sẽ sử dụng các Domain Event trong một Fabric như thế nào? Như đã thảo luận trong chương Domain Events (8), các Aggregate của bạn sẽ sử dụng một component (thành phần) `DomainEventPublisher` đơn giản. Trong bộ nhớ đệm của Fabric, bộ xuất bản này có thể chỉ cần đẩy các Event đã phát vào một cache/region chuyên biệt. Các Event được lưu tạm này sau đó sẽ được phân phối tới những đối tượng đăng ký (subscriber / listener), theo hình thức đồng bộ hoặc bất đồng bộ. Để tránh lãng phí dung lượng bộ nhớ quý giá trong vùng cache/region dành riêng cho Event này, khi mỗi Event đã được tất cả các subscriber xác nhận xử lý thành công (fully acknowledged), bản ghi của nó sẽ bị xóa khỏi map. Dĩ nhiên, một Event chỉ được coi là đã xác nhận hoàn tất khi nó đã được một hoặc nhiều subscriber đẩy lên một message queue (hàng đợi thông điệp) hoặc bus, và/hoặc được sử dụng để làm mới query model (mô hình truy vấn) của CQRS.

Vì các bên đăng ký Domain Event cũng có thể sử dụng những sự kiện này để thực hiện việc đồng bộ hóa các Aggregate phụ thuộc khác, nên tính nhất quán sau cùng (eventual consistency) hoàn toàn được đảm bảo thông qua cấu trúc kiến trúc.

## Truy vấn liên tục (Continuous Queries)

Một số Fabric hỗ trợ một dạng thông báo sự kiện được gọi là Continuous Query (truy vấn liên tục). Cơ chế này cho phép client đăng ký một truy vấn với Fabric nhằm đảm bảo rằng client sẽ nhận được thông báo về bất kỳ thay đổi nào trong cache thỏa mãn truy vấn đó. Một ứng dụng điển hình của Continuous Query là dành cho các thành phần giao diện người dùng (UI), giúp chúng lắng nghe các thay đổi có thể ảnh hưởng đến giao diện hiển thị hiện tại.

Bạn có nhận ra điều gì sắp tới không? CQRS có độ tương thích rất cao với tính năng Continuous Query, giả định rằng query model được duy trì trực tiếp trong Fabric. Thay vì bắt khung nhìn (view) phải liên tục săn lùng các bản cập nhật bảng dữ liệu hiển thị, các thông báo được gửi về từ những Continuous Query đã đăng ký sẽ được xử lý kịp thời, cho phép các view cập nhật trạng thái đúng lúc (just in time). Dưới đây là ví dụ về một client đăng ký nhận các sự kiện Continuous Query trong GemFire:

```java
CqAttributesFactory factory = new CqAttributesFactory();
CqListener listener = new BacklogItemWatchListener();
factory.addCqListener(listener);

String continuousQueryName = "BacklogItemWatcher";
String query = "select * from /queryModelBacklogItem qmbli " +
               "where qmbli.status = 'Committed'";

CqQuery backlogItemWatcher =
    queryService.newCq(continuousQueryName, query, factory.create());

```

Giờ đây, Data Fabric sẽ phân phối các cập nhật của CQRS query model (dựa trên các sửa đổi ở Aggregate) tới đối tượng callback phía client do `CqListener` cung cấp, kèm theo các metadata (siêu dữ liệu) về những dữ liệu đã được thêm, cập nhật hoặc xóa bỏ khi các tiêu chí so khớp được thỏa mãn.

## Xử lý phân tán (Distributed Processing)

Một ứng dụng mạnh mẽ khác của Data Fabric là phân tán việc xử lý dữ liệu trên khắp các vùng cache đã được sao chép của Fabric rồi trả kết quả tổng hợp về cho client. Khả năng này giúp Fabric hiện thực hóa mô hình xử lý song song phân tán hướng sự kiện, có thể thông qua việc sử dụng các Long-Running Process.

Để minh họa tính năng này, chúng ta cần đề cập đến một số phương pháp triển khai cụ thể trong GemFire và Coherence. Bộ điều hành tiến trình (Process executive) của bạn có thể được triển khai dưới dạng một GemFire `Function` hoặc một Coherence `Entry Processor`. Cả hai đều có thể đóng vai trò như các trình xử lý Command (lệnh) [Gamma et al.] thực thi song song trên khắp vùng cache phân tán đã được sao chép. (Bạn cũng có thể xem khái niệm này như một Domain Service (dịch vụ miền), dù những gì nó thực hiện có thể không hoàn toàn xoay quanh nghiệp vụ cốt lõi). Để nhất quán, chúng ta hãy gọi tính năng này là Function. Một Function có thể tùy ý tiếp nhận một bộ lọc (filter) để giới hạn phạm vi thực thi chỉ đối với các thể hiện Aggregate phù hợp.

Hãy xem một Function mẫu triển khai Long-Running Process cho quy trình Phone Number Count Process (Quy trình đếm số điện thoại) đã được giới thiệu trước đó. Quy trình này sẽ được thực thi song song trên khắp vùng cache đã sao chép bằng cách sử dụng một GemFire Function:

```java
public class PhoneNumberCountSaga extends FunctionAdapter {
    @Override
    public void execute(FunctionContext context) {
        Cache cache = CacheFactory.getAnyInstance();
        QueryService queryService = cache.getQueryService();
        String phoneNumberFilterQuery = (String) context.getArguments();

        ...
        // Mã giả (Pseudo code)
        // - Thực thi Function để lấy MatchedPhoneNumbersCounted.
        //   - Gửi kết quả tới aggregator bằng cách gọi
        //     aggregator.sendResult(MatchedPhoneNumbersCounted).
        // - Thực thi Function để lấy AllPhoneNumbersCounted.
        //   - Gửi kết quả tới aggregator bằng cách gọi
        //     aggregator.sendResult(AllPhoneNumbersCounted).
        // - Aggregator tự động tích lũy các phản hồi
        //   từ mỗi lệnh gọi Function phân tán và trả về
        //   một kết quả tổng hợp duy nhất cho client.
    }
}

```

Dưới đây là đoạn mã mẫu cho một client thực thi một Long-Running Process song song trên vùng cache phân tán đã được sao chép:

```java
PhoneNumberCountProcess phoneNumberCountProcess = new PhoneNumberCountProcess();

```

```java
String phoneNumberFilterQuery =
    "select phoneNumber from /phoneNumberRegion pnr " +
    "where pnr.areaCode = '303'";

Execution execution =
    FunctionService.onRegion(phoneNumberRegion)
        .withFilter(0)
        .withArgs(phoneNumberFilterQuery)
        .withCollector(new PhoneNumberCountResultCollector());

PhoneNumberCountResultCollector resultCollector =
    execution.execute(phoneNumberCountProcess);

List allPhoneNumberCountResults = (List) resultsCollector.getResult();

```

Dĩ nhiên, quy trình thực tế có thể phức tạp hơn rất nhiều hoặc đơn giản hơn ví dụ này. Điều này cũng chứng minh rằng một Process không nhất thiết phải là một khái niệm thuần túy hướng sự kiện, mà nó còn có thể tương thích với các cách tiếp cận xử lý đồng thời, phân tán khác. Để nắm được thảo luận toàn diện về việc xử lý song song và phân tán dựa trên Fabric, hãy xem [GemFire Functions].

## Tổng kết (Wrap-Up)

Chúng ta đã điểm qua một số phong cách kiến trúc và mẫu kiến trúc có thể kết hợp cùng DDD. Đây chưa phải là một danh sách vét cạn bởi số lượng khả năng ứng dụng là vô cùng phong phú, điều này càng làm nổi bật tính linh hoạt của DDD. Chẳng hạn, chúng ta chưa bàn đến cách áp dụng DDD khi kết hợp cùng mô hình Map-Reduce. Đó sẽ là chủ đề cho các cuộc thảo luận trong tương lai.

* Chúng ta đã thảo luận về Layers Architecture (kiến trúc phân lớp) truyền thống và cách cải tiến nó thông qua Nguyên lý Đảo ngược Phụ thuộc (Dependency Inversion Principle).
* Bạn đã tìm hiểu về sức mạnh của Hexagonal Architecture (kiến trúc lục giác) — một phong cách kiến trúc trường tồn, đóng vai trò là phong cách bao quát cho kiến trúc của các ứng dụng.
* Chúng ta đã nhấn mạnh cách DDD được vận dụng trong môi trường SOA (Service-Oriented Architecture — kiến trúc hướng dịch vụ), với REST, cũng như khi sử dụng một Data Fabric hoặc Grid-Based Distributed Cache (bộ nhớ đệm phân tán dạng lưới).
* Bạn đã có cái nhìn tổng quan về CQRS và cách nó giúp đơn giản hóa một số khía cạnh của ứng dụng.
* Chúng ta đã xem xét các khía cạnh đa dạng trong cơ chế hoạt động của kiến trúc hướng sự kiện, bao gồm Pipes and Filters (đường ống và bộ lọc), Long-Running Process, và cả một cái nhìn thoáng qua về Event Sourcing (nguồn sự kiện).

Tiếp theo, chúng ta sẽ bước sang chuỗi các chương nói về tactical modeling (mô hình hóa chiến thuật) trong DDD. Những chương này sẽ giúp bạn nhìn thấy các lựa chọn mô hình hóa ở mức độ chi tiết hơn nằm trong tầm tay mình, cùng cách vận dụng chúng đạt hiệu quả cao nhất.

Trang này cố tình để trống

## Chapter 5

## Entities

Tôi là Chevy Chase . . . còn bạn thì không. -Chevy Chase

> 💡 **Giải thích thêm:** Câu nói này là lời chào mở đầu kinh điển của danh hài Chevy Chase trong chuyên mục *Weekend Update* của chương trình truyền hình *Saturday Night Live* (SNL) vào thập niên 1970. Tác giả trích dẫn câu nói này ở đầu chương về Entities (Thực thể) nhằm nhấn mạnh một chân lý nền tảng: Một Entity được xác định duy nhất bởi **danh tính (identity)** của chính nó. Dù hai đối tượng có ngoại hình, thuộc tính hay dữ liệu giống nhau đến đâu, thì "Tôi là tôi, và bạn không phải là tôi" — danh tính của một Entity là bất biến và tách biệt tuyệt đối với tất cả các đối tượng khác.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Các lập trình viên thường có xu hướng tập trung vào dữ liệu thay vì miền nghiệp vụ (domain). Điều này rất dễ xảy ra với những người mới tiếp cận DDD, xuất phát từ các phương pháp phát triển phần mềm phổ biến vốn đặt nặng tầm quan trọng vào cơ sở dữ liệu. Thay vì thiết kế các khái niệm nghiệp vụ với hành vi phong phú (rich behaviors), chúng ta lại suy nghĩ chủ yếu về các thuộc tính (cột) và quan hệ liên kết (khóa ngoại) của dữ liệu. Cách làm này vô tình ánh xạ nguyên xi mô hình dữ liệu sang các đối tượng tương ứng, dẫn tới việc hầu như mọi khái niệm trong "domain model" đều bị biến thành một Entity tràn ngập các phương thức getter và setter. Rất dễ để tìm thấy những công cụ có thể tự động sinh ra toàn bộ những thứ đó cho chúng ta. Mặc dù các hàm truy xuất thuộc tính (property accessor) không có gì sai trái, nhưng đó hoàn toàn không phải là hành vi duy nhất mà một Entity trong DDD nên có.

Đó chính là cái bẫy mà các lập trình viên tại SaaSOvation đã mắc phải. Hãy rút ra bài học từ những kinh nghiệm thiết kế Entity của họ.

## Lộ trình của chương này (Road Map to This Chapter)

* Xem xét lý do tại sao Entity có vị trí thích hợp khi chúng ta cần mô hình hóa những sự vật mang tính độc nhất.
* Tìm hiểu cách thức sinh ra định danh duy nhất (unique identity) cho các Entity.
* Tham quan một buổi thiết kế khi đội ngũ phát triển nắm bắt Ubiquitous Language (Ngôn ngữ Chung) (1) vào thiết kế Entity.
* Học cách thể hiện vai trò và trách nhiệm của Entity.
* Xem các ví dụ về cách xác thực (validate) Entity và lưu trữ chúng vào hệ thống persistence.

## Tại sao chúng ta sử dụng Entity (Why We Use Entities)

Chúng ta thiết kế một khái niệm nghiệp vụ dưới dạng một Entity khi chúng ta quan tâm đến tính cá thể (individuality) của nó, tức là khi việc phân biệt nó với tất cả các đối tượng khác trong hệ thống là một ràng buộc bắt buộc. Một Entity là một thực thể độc nhất và có khả năng biến đổi liên tục trong suốt một khoảng thời gian dài. Những thay đổi có thể sâu rộng đến mức đối tượng trông dường như khác hoàn toàn so với trạng thái ban đầu của nó. Tuy nhiên, xét về mặt định danh, nó vẫn chính là đối tượng đó.

Khi đối tượng thay đổi, chúng ta có thể quan tâm đến việc theo vết xem các thay đổi được thực hiện khi nào, như thế nào và bởi ai. Hoặc chúng ta có thể chỉ cần trạng thái hiện tại của nó phản ánh đủ về các bước chuyển trạng thái trước đó mà không cần theo dõi thay đổi một cách tường minh. Ngay cả khi không quyết định theo dõi từng chi tiết trong lịch sử thay đổi, chúng ta vẫn có thể lập luận và thảo luận về chuỗi các thay đổi hợp lệ có thể diễn ra với những đối tượng này trong suốt vòng đời của chúng. Chính định danh duy nhất và đặc tính có thể biến đổi (mutability) là những yếu tố phân biệt Entity với Value Object (đối tượng giá trị) (6).

Có những thời điểm Entity không phải là công cụ mô hình hóa phù hợp để lựa chọn. Việc lạm dụng hoặc sử dụng sai mục đích xảy ra thường xuyên hơn nhiều so với những gì mọi người tưởng. Thông thường, một khái niệm nên được mô hình hóa dưới dạng một Value (Giá trị). Nếu bạn cảm thấy bất đồng với quan điểm này, rất có thể DDD không phù hợp với nhu cầu nghiệp vụ của bạn. Hoàn toàn có khả năng một hệ thống thuần CRUD (Create, Read, Update, Delete) sẽ thích hợp hơn. Nếu đúng như vậy, quyết định chọn CRUD sẽ tiết kiệm cho dự án của bạn cả thời gian lẫn tiền bạc. Vấn đề là việc theo đuổi các giải pháp thay thế dựa trên CRUD không phải lúc nào cũng bảo toàn được những nguồn tài nguyên quý giá đó.

Các doanh nghiệp thường xuyên dồn quá nhiều công sức vào việc phát triển những bộ chỉnh sửa bảng cơ sở dữ liệu được "thần thánh hóa" (glorified database table editors). Nếu không chọn đúng công cụ, các giải pháp dựa trên CRUD khi được xử lý quá cầu kỳ sẽ trở nên vô cùng đắt đỏ. Khi CRUD thực sự là lựa chọn hợp lý, các ngôn ngữ và framework như Groovy và Grails, Ruby on Rails cùng các công nghệ tương tự sẽ phát huy giá trị cao nhất. Nếu lựa chọn chuẩn xác, nó chắc chắn sẽ tiết kiệm cả thời gian và tiền bạc.

## Logic kiểu cao bồi (Cowboy Logic)

* AJ:    'Tôi vừa dẫm phải cái thứ CRUD/rác rưởi quái quỷ gì thế này?'
* LB:    'Đấy là một bãi phân bò (cow pie) đấy, J!'
* AJ:    'Tôi thừa biết bánh pie là gì nhé. Nào là bánh táo (apple pie), rồi bánh anh đào (cherry pie). Cái của nợ này đời nào là bánh pie!'
* LB:    'Như các cụ vẫn bảo đấy: "Đừng bao giờ đá vào bãi phân bò lúc trời nắng chang chang". May cho cậu là cậu chưa sút vào nó đấy.'

> 💡 **Giải thích thêm:** Đoạn hội thoại này chứa đựng màn châm biếm chơi chữ nhiều tầng:
> 1. Chơi chữ từ **CRUD**: Vừa là từ viết tắt kỹ thuật (Create, Read, Update, Delete), vừa là từ lóng tiếng Anh đồng âm *crud* mang nghĩa là thứ bẩn thỉu, rác rưởi, cặn bã. AJ than phiền mình vừa dẫm phải "thứ rác rưởi/CRUD", ám chỉ sự thất vọng khi sa lầy vào một hệ thống CRUD luộm thuộm.
> 2. Chơi chữ từ **Cow pie**: Tiếng lóng chỉ bãi phân bò khô trên đồng cỏ có hình dạng tròn dẹt giống chiếc bánh nướng (pie).
> 3. Thành ngữ *"Never kick a cow pie on a hot day"* (Đừng bao giờ đá vào bãi phân bò vào ngày trời nắng): Vào ngày nắng gắt, bãi phân bò se khô lớp vỏ bên ngoài nhưng bên trong vẫn ướt mềm; nếu đá vào, nó sẽ vỡ toang làm bẩn người đá. Trong kỹ thuật phần mềm, tác giả mượn ẩn dụ này để cảnh báo: Đừng vội vàng can thiệp hay "đụng chạm" vào một hệ thống mã nguồn legacy/CRUD trông có vẻ khô ráo, ổn định bên ngoài nhưng bên trong đầy rẫy rắc rối, nếu bạn chưa thực sự hiểu rõ bản chất.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)
> 
> 

Mặt khác, nếu chúng ta áp dụng CRUD cho những hệ thống không phù hợp — những hệ thống phức tạp hơn, xứng đáng với sự chuẩn xác của DDD — chúng ta có thể sẽ phải hối hận. Khi độ phức tạp gia tăng, chúng ta sẽ nếm trải những hạn chế do việc chọn sai công cụ. Các hệ thống CRUD không thể tạo ra một mô hình nghiệp vụ tinh tế nếu chỉ đơn thuần ghi nhận dữ liệu.

Nếu DDD là một khoản đầu tư chính đáng mang lại lợi ích thiết thực cho doanh nghiệp, chúng ta hãy sử dụng Entity đúng như mục đích vốn có của nó.

Khi một đối tượng được phân biệt bởi định danh thay vì các thuộc tính của nó, hãy đặt điều này làm trọng tâm hàng đầu trong định nghĩa của đối tượng trong mô hình. Giữ cho định nghĩa lớp đơn giản và tập trung vào tính liên tục của vòng đời cùng định danh của nó. Hãy xác định một phương thức để phân biệt từng đối tượng bất kể hình thức hay lịch sử biến đổi của nó. . . . Mô hình phải định nghĩa rõ thế nào là hai đối tượng cùng là một thực thể. [Evans, tr. 92]

Chương này sẽ hướng dẫn cách đặt sự chú trọng đúng mực vào các Entity và chỉ cho bạn thấy những kỹ thuật thiết kế Entity khác nhau.

## Định danh duy nhất (Unique Identity)

Trong những giai đoạn đầu của việc thiết kế một Entity, chúng ta chủ đích chỉ tập trung vào các thuộc tính và hành vi cơ bản đóng vai trò cốt lõi đối với định danh duy nhất của nó, cũng như những thuộc tính hữu ích cho việc truy vấn, đồng thời cố tình bỏ qua mọi thuộc tính và hành vi khác cho đến khi chúng ta đã thống nhất được các yếu tố cốt lõi đó.

Thay vì chỉ chăm chăm vào các thuộc tính hay thậm chí là hành vi, hãy gọt giũa định nghĩa của đối tượng Entity về những đặc tính bản chất nhất, đặc biệt là những yếu tố giúp nhận diện nó hoặc thường được dùng để tìm kiếm, đối soát. Chỉ bổ sung những hành vi thực sự thiết yếu đối với khái niệm đó và các thuộc tính mà hành vi đó yêu cầu. [Evans, tr. 93]

Vì vậy, đó là điều đầu tiên chúng ta sẽ thực hiện. Việc nắm giữ một loạt các tùy chọn khả dĩ để triển khai định danh là điều thực sự quan trọng, tương tự như các phương án nhằm đảm bảo tính độc nhất luôn được duy trì xuyên suốt thời gian.

Định danh duy nhất của một Entity có thể tiện lợi hoặc không tiện lợi cho việc tìm kiếm hoặc đối soát. Việc sử dụng định danh duy nhất để so khớp thường phụ thuộc vào mức độ thân thiện với con người (human-readable) của nó. Ví dụ, nếu ứng dụng cung cấp tính năng tìm kiếm theo tên người cho người dùng, rất khó có khả năng tên đó được sử dụng làm định danh duy nhất cho Entity `Person`. Con người rất hay trùng tên nhau. Mặt khác, nếu ứng dụng cho phép tìm kiếm mã số thuế của một công ty, mã số thuế đó hoàn toàn có thể là mã định danh duy nhất chính yếu cho Entity `Company`. Các chính phủ luôn cấp các mã số thuế duy nhất.

Value Object có thể đóng vai trò là vật chứa đựng (holder) của định danh duy nhất. Chúng mang tính bất biến (immutable), giúp đảm bảo tính ổn định của định danh, đồng thời mọi hành vi đặc thù gắn liền với loại định danh đó đều được gom về một mối. Việc sở hữu một điểm hội tụ cho các hành vi liên quan đến định danh, dù đơn giản đến đâu, cũng sẽ giúp ngăn không cho các tri thức chuyên biệt này bị rò rỉ sang các phần khác của mô hình và phía client.

Hãy xem xét một số chiến lược tạo định danh phổ biến, từ những cách đơn giản và cơ bản nhất cho đến những cách có độ phức tạp tăng dần:

* Người dùng cung cấp một hoặc nhiều giá trị duy nhất ban đầu dưới dạng đầu vào cho ứng dụng. Ứng dụng phải đảm bảo rằng chúng là duy nhất.

* Ứng dụng tự sinh định danh nội bộ bằng một thuật toán đảm bảo tính độc nhất. Chúng ta có thể nhờ một thư viện hoặc framework làm việc này thay mình, nhưng bản thân ứng dụng hoàn toàn có thể tự xử lý.
* Ứng dụng dựa vào một kho lưu trữ dữ liệu (persistence store), chẳng hạn như cơ sở dữ liệu, để sinh định danh duy nhất.
* Một Bounded Context (ngữ cảnh giới hạn) (2) khác (hệ thống hoặc ứng dụng khác) đã xác định sẵn định danh duy nhất. Giá trị này được người dùng nhập vào hoặc lựa chọn từ một tập danh sách có sẵn.

Chúng ta hãy cùng xem xét từng chiến lược riêng lẻ, cùng với những thách thức cụ thể đi kèm mỗi loại. Luôn có những tác dụng phụ khi cân nhắc các giải pháp kỹ thuật khác nhau. Một trong những tác dụng phụ điển hình xuất hiện khi chúng ta sử dụng cơ sở dữ liệu quan hệ để lưu trữ đối tượng, khiến các chi tiết kỹ thuật bị rò rỉ vào trong domain model. Chúng ta sẽ khép lại các mối bận tâm về việc tạo định danh bằng cách giải quyết tác động từ thời điểm sinh định danh, định danh tham chiếu của cơ sở dữ liệu quan hệ lên các đối tượng miền, và vai trò của kỹ thuật ánh xạ đối tượng - quan hệ (Object-Relational Mapping — ORM) trong tình huống này. Chúng ta cũng sẽ cân nhắc một số chỉ dẫn thực tế để duy trì tính ổn định của các định danh duy nhất.

## Người dùng cung cấp định danh (User Provides Identity)

Việc để người dùng tự nhập tay thông tin chi tiết của định danh duy nhất thoạt nhìn có vẻ là một cách tiếp cận trực tiếp và đơn giản. Người dùng gõ một giá trị hoặc ký hiệu dễ nhận biết vào trường nhập liệu hoặc chọn từ một tập hợp các đặc tính có sẵn, và Entity được khởi tạo. Đúng là cách tiếp cận này đủ đơn giản. Tuy nhiên, nó có thể kéo theo nhiều rắc rối phức tạp.

Một điểm phức tạp nằm ở việc phụ thuộc vào người dùng để tạo ra các định danh chất lượng. Định danh có thể là duy nhất nhưng lại sai sót về mặt nội dung. Trong hầu hết các trường hợp, định danh bắt buộc phải mang tính bất biến, nghĩa là người dùng không được phép sửa đổi chúng. Tuy nhiên, không phải lúc nào cũng như vậy, và đôi khi việc cho phép người dùng đính chính lại giá trị định danh cũng mang lại những lợi ích nhất định. Dưới đây là một ví dụ. Nếu chúng ta sử dụng tiêu đề của Forum (Diễn đàn) và Discussion (Thảo luận) làm định danh duy nhất, điều gì sẽ xảy ra nếu người dùng gõ sai chính tả tiêu đề, hoặc sau đó nhận thấy tiêu đề chưa thực sự phù hợp như mong muốn, như được minh họa trong Hình 5.1? Cái giá phải trả cho việc thay đổi là gì? Dù định danh do người dùng cung cấp có vẻ là một phương án tiết kiệm chi phí, nhưng thực tế có thể không phải vậy. Liệu chúng ta có thể tin tưởng vào người dùng trong việc tạo ra các định danh vừa duy nhất, vừa chính xác và bền vững theo thời gian hay không?

Việc ngăn ngừa vấn đề này bắt đầu từ các cuộc thảo luận thiết kế. Các nhóm phát triển cần cân nhắc những phương pháp chống sai sót (fail-proof) để hỗ trợ người dùng xác định định danh duy nhất. Quy trình phê duyệt định danh dựa trên workflow (luồng công việc) không thích hợp cho các miền nghiệp vụ có thông lượng cao (high-throughput), nhưng lại phát huy hiệu quả tốt nhất khi định danh bắt buộc phải thân thiện với con người. Nếu việc tạo và phê duyệt một định danh — vốn sẽ được sử dụng rộng khắp doanh nghiệp trong nhiều năm tới — đòi hỏi thêm thời gian và công sức, đồng thời hệ thống có thể hỗ trợ một workflow như vậy, thì việc bỏ thêm vài chu kỳ để đảm bảo chất lượng của định danh là một khoản đầu tư xứng đáng.

Hình 5.1 Tiêu đề diễn đàn bị sai chính tả và tiêu đề cuộc thảo luận chưa thực sự phù hợp.

Chúng ta luôn có tùy chọn lưu giữ các giá trị do người dùng nhập dưới dạng các thuộc tính của Entity phục vụ mục đích tìm kiếm, đối soát, nhưng không dùng chúng làm định danh duy nhất. Các thuộc tính đơn giản sẽ dễ dàng chỉnh sửa hơn như một phần trạng thái vận hành bình thường của Entity vốn thay đổi theo thời gian. Trong trường hợp đó, chúng ta sẽ cần sử dụng phương thức khác để thu thập định danh duy nhất.

## Ứng dụng tự sinh định danh (Application Generates Identity)

Có những cách thức vô cùng tin cậy để tự động sinh định danh duy nhất, dẫu vậy cần phải cẩn trọng khi ứng dụng được triển khai theo cụm (clustered) hoặc phân tán trên nhiều node tính toán. Tồn tại những pattern tạo định danh có thể đảm bảo với độ tin cậy rất cao việc tạo ra một định danh duy nhất tuyệt đối. UUID (Universally Unique Identifier — mã định danh duy nhất toàn cục), hay GUID (Globally Unique Identifier), là một phương pháp như vậy. Dưới đây là một biến thể phổ biến, trong đó kết quả của từng bước được ghép lại thành một chuỗi biểu diễn dạng văn bản duy nhất:

1. Thời gian tính theo mili-giây trên node tính toán
2. Địa chỉ IP của node tính toán
3. Định danh đối tượng (Object identity) của thể hiện đối tượng factory bên trong máy ảo (Java)
4. Số ngẫu nhiên được sinh ra bởi cùng một bộ sinh số ngẫu nhiên bên trong máy ảo (Java)

Cách này tạo ra một giá trị duy nhất 128-bit. Nó thường được biểu diễn dưới dạng một chuỗi văn bản mã hóa thập lục phân (hexadecimal) dài 32-byte hoặc 36-byte. Định dạng chuỗi văn bản sẽ dài 36 byte nếu bạn sử dụng dấu gạch nối thông thường để phân tách các đoạn theo định dạng `f36ab21c-67dc-5274-c642-1de2f4d5e72a`. Nếu không có dấu gạch nối, nó dài 32 byte. Dù theo cách nào, định danh này cũng có kích thước lớn và không được xem là thân thiện với con người.

Trong thế giới Java, công thức này đã được thay thế bằng bộ sinh UUID tiêu chuẩn có sẵn kể từ Java 1.5. Nó được cung cấp bởi lớp `java.util.UUID`. Bản triển khai này hỗ trợ bốn thuật toán sinh khác nhau dựa trên biến thể Leach-Salz. Sử dụng API tiêu chuẩn của Java, chúng ta có thể dễ dàng tạo ra một định danh duy nhất giả ngẫu nhiên:

```java
String rawId = java.util.UUID.randomUUID().toString();

```

Lệnh này sử dụng UUID loại 4 (type 4), vận dụng một bộ sinh số giả ngẫu nhiên mạnh về mặt mật mã học (cryptographically strong), dựa trên bộ sinh `java.security.SecureRandom`. Loại 3 (type 3) sử dụng phương pháp mã hóa theo tên, vận dụng `java.security.MessageDigest`. Chúng ta có thể tạo một UUID dựa trên tên như sau:

```java
String rawId = java.util.UUID.nameUUIDFromBytes(

```

```java
    "Some text".getBytes()).toString();

```

Chúng ta cũng có thể kết hợp việc sinh số giả ngẫu nhiên với mã hóa:

```java
SecureRandom randomGenerator = new SecureRandom();
int randomNumber = randomGenerator.nextInt();
String randomDigits = new Integer(randomNumber).toString();
MessageDigest encryptor = MessageDigest.getInstance("SHA-1");

```

```java
byte[] rawIdBytes = encryptor.digest(randomDigits.getBytes());

```

Bây giờ nhiệm vụ còn lại duy nhất là chuyển đổi mảng `rawIdBytes` thành dạng biểu diễn chuỗi văn bản thập lục phân. Chúng ta có thể tận dụng việc chuyển đổi này mà không tốn công sức. Sau khi sinh số ngẫu nhiên và chuyển nó thành một `String`, chúng ta truyền chuỗi văn bản đó vào phương thức Factory [Gamma et al.] `nameUUIDFromBytes()` của lớp `UUID`.

Ngoài ra còn có các công cụ sinh định danh khác như `java.rmi.server.UID` và `java.rmi.dgc.VMID`, nhưng chúng có vẻ kém ưu việt hơn `java.util.UUID` nên sẽ không được bàn luận ở đây.

UUID là loại định danh có tốc độ sinh tương đối nhanh, không đòi hỏi tương tác với bên ngoài, chẳng hạn như cơ chế lưu trữ persistence. Ngay cả khi một loại Entity cụ thể được khởi tạo hàng chục, hàng trăm lần mỗi giây, bộ sinh UUID vẫn bắt kịp tốc độ đó. Đối với các miền nghiệp vụ đòi hỏi hiệu năng cao hơn, chúng ta có thể lưu sẵn một số lượng nhất định các thể hiện UUID trong cache và nạp thêm vào cache ở chế độ chạy nền (background). Nếu các thể hiện UUID được lưu tạm bị mất do khởi động lại máy chủ, điều đó cũng không tạo ra các khoảng trống trong chuỗi định danh, vì tất cả chúng đều dựa trên các giá trị ngẫu nhiên được sinh độc lập. Việc nạp lại cache khi máy chủ khởi động lại sẽ không gây ra bất kỳ hệ lụy tiêu cực nào từ các giá trị bị bỏ sót.

Với kích thước định danh lớn như vậy, việc sử dụng nó trong một số trường hợp hiếm hoi có thể trở nên thiếu thực tế do chi phí tiêu tốn bộ nhớ (memory overhead). Trong những tình huống đó, một định danh kiểu số nguyên dài (long) 8-byte do cơ chế persistence sinh ra sẽ cải thiện tình hình. Một số nguyên 4-byte nhỏ hơn, với khoảng hai tỷ giá trị duy nhất, thậm chí cũng có thể đáp ứng đủ nhu cầu. Những cách tiếp cận này sẽ được thảo luận ở phần tiếp theo.

Xem xét ví dụ dưới đây, hoàn toàn dễ hiểu khi thông thường chúng ta không muốn hiển thị một chuỗi UUID lên giao diện người dùng:

```
f36ab21c-67dc-5274-c642-1de2f4d5e72a

```

Một chuỗi UUID đầy đủ thường chỉ phù hợp khi nó có thể được ẩn đi khỏi tầm mắt người dùng và thay thế bằng các kỹ thuật tham chiếu thân thiện với con người. Ví dụ, chúng ta có thể thiết kế các tài nguyên hypermedia (siêu phương tiện) với URI có thể gửi qua email hoặc chuyển tiếp qua các hình thức nhắn tin giữa người dùng với nhau. Phần văn bản liên kết có thể được dùng để ngụy trang cho chuỗi UUID trông có phần bí ẩn, tương tự như cách đoạn text trong thẻ `<a>text</a>` che đi các liên kết kỹ thuật trong HTML.

Tùy thuộc vào mức độ tin cậy của bạn đối với tính duy nhất của từng phân đoạn riêng lẻ trong chuỗi UUID dạng văn bản thập lục phân, bạn có thể quyết định chỉ sử dụng một hoặc một vài phân đoạn của chuỗi đó. Các định danh rút gọn này sẽ đáng tin cậy hơn khi chỉ được sử dụng làm định danh cục bộ (local identity) của các Entity nằm bên trong ranh giới của Aggregate (10). Định danh cục bộ có nghĩa là các Entity nằm bên trong một Aggregate chỉ cần đảm bảo tính duy nhất so với các Entity khác trong cùng Aggregate đó. Ngược lại, Entity đóng vai trò là Aggregate Root (Gốc kết tập) luôn bắt buộc phải có định danh duy nhất toàn cục.

Bộ sinh định danh tự xây dựng của chúng ta có thể sử dụng một hoặc nhiều phân đoạn UUID cụ thể. Hãy xem một ví dụ giả định: `APM-P-08-14-2012-F36AB21C`. Định danh dài 25 ký tự này đại diện cho một Sản phẩm (`P` — Product) thuộc Ngữ cảnh Quản lý Dự án Linh hoạt (`APM` — Agile Project Management Context) được tạo vào ngày 14 tháng 8 năm 2012. Đoạn văn bản phụ `F36AB21C` là phân đoạn đầu tiên của một UUID được sinh ra, giúp nó phân biệt duy nhất với các Entity Product khác được tạo trong cùng ngày. Nó vừa mang lại lợi ích thân thiện, dễ đọc với con người, vừa có xác suất rất cao về tính duy nhất toàn cục. Người dùng không phải là đối tượng duy nhất hưởng lợi. Khi những định danh như thế này được truyền qua lại giữa các Bounded Context, các lập trình viên có thể biết ngay nguồn gốc xuất xứ của chúng. Đối với SaaSOvation, cách tiếp cận này có thể mang tính thực tiễn cao vì các Aggregate còn được phân tách sâu hơn theo từng tenant (khách thuê/đơn vị thuê hệ thống).

Việc lưu trữ loại định danh này trong một biến kiểu `String` có lẽ không phải là một lựa chọn sáng suốt. Một Value Object tùy biến dành riêng cho định danh sẽ hoạt động hiệu quả hơn:

```java
String rawId = "APM-P-08-14-2012-F36AB21C"; // sẽ được tự động sinh
ProductId productId = new ProductId(rawId);
...
Date productCreationDate = productId.creationDate();

```

Client có thể truy vấn các thông tin chi tiết về định danh, chẳng hạn như ngày sản phẩm được tạo, và thông tin đó sẽ được cung cấp một cách tiện lợi. Phía client không cần phải hiểu định dạng chuỗi thô của định danh. Giờ đây, Aggregate Root `Product` có thể cung cấp ngày tạo của nó mà không cần để lộ cho client biết cách thức lấy thông tin đó ra sao:

```java
public class Product extends Entity {
    private ProductId productId;
    ...
    public Date creationDate() {
        return this.productId().creationDate();
    }
    ...
}

```

Bạn có thể tìm thấy các cơ chế sinh định danh trong các thư viện và framework của bên thứ ba. Dự án Apache Commons có thành phần Commons Id (sandbox), cung cấp năm bộ sinh định danh khác nhau.

Một số kho lưu trữ persistence, chẳng hạn như các cơ sở dữ liệu NoSQL như Riak và MongoDB, có thể tự động sinh định danh cho bạn. Thông thường để lưu một giá trị trong Riak, bạn sử dụng phương thức HTTP `PUT` kèm theo một key:

```
PUT /riak/bucket/key [object serialization]

```

Thay vào đó, bạn có thể dùng `POST` mà không cần cung cấp key, buộc Riak phải tự tạo một định danh duy nhất. Dẫu vậy, chúng ta vẫn cần phải cân nhắc giữa việc sinh định danh sớm (early) hay sinh định danh muộn (late), như sẽ được thảo luận ở phần sau của chương này.

Thành phần nào sẽ đóng vai trò là Factory để tạo ra các định danh do ứng dụng sinh? Đối với việc sinh định danh cho Aggregate Root, tôi thích sử dụng chính Repository (12) của nó:

```java
public class HibernateProductRepository implements ProductRepository {
    ...
    public ProductId nextIdentity() {
        return new ProductId(
            java.util.UUID.randomUUID().toString().toUpperCase());
    }
    ...
}

```

Đây có vẻ là một vị trí hoàn toàn tự nhiên để thực hiện việc sinh định danh.

## Cơ chế lưu trữ sinh định danh (Persistence Mechanism Generates Identity)

Việc ủy quyền sinh định danh duy nhất cho một cơ chế lưu trữ persistence mang lại một số lợi thế đặc thù. Nếu chúng ta yêu cầu cơ sở dữ liệu cung cấp một sequence (chuỗi số tuần tự) hoặc giá trị tự tăng (auto-incrementing value), giá trị đó luôn luôn đảm bảo tính duy nhất.

Tùy thuộc vào phạm vi giá trị cần thiết, cơ sở dữ liệu có thể sinh ra giá trị duy nhất với kích thước 2-byte, 4-byte hoặc 8-byte. Trong Java, kiểu số nguyên ngắn `short` 2-byte cho phép tạo tối đa 32.767 định danh duy nhất; kiểu số nguyên thông thường `int` 4-byte mang lại 2.147.483.647 giá trị duy nhất; và kiểu số nguyên dài `long` 8-byte sẽ cung cấp tới 9.223.372.036.854.775.807 định danh khác biệt. Ngay cả các chuỗi biểu diễn dạng văn bản được chèn số 0 ở đầu (zero-filled) cho các dải giá trị này cũng rất gọn gàng, lần lượt là 5, 10 và 19 ký tự. Chúng cũng có thể được tận dụng để tạo thành các định danh phức hợp (composite identity).

Một nhược điểm tiềm ẩn là vấn đề hiệu năng. Việc phải truy vấn xuống cơ sở dữ liệu để lấy từng giá trị có thể mất nhiều thời gian hơn đáng kể so với việc tự sinh định danh ngay bên trong ứng dụng. Mọi thứ phụ thuộc nhiều vào tải của cơ sở dữ liệu và nhu cầu của ứng dụng. Một giải pháp khắc phục là lưu tạm (cache) các giá trị sequence/tự tăng ngay trong ứng dụng, chẳng hạn như trong một Repository. Cách này có thể hoạt động tốt, nhưng thông thường chúng ta phải chấp nhận việc mất đi một số lượng đáng kể các giá trị chưa được sử dụng mỗi khi các node máy chủ phải khởi động lại. Nếu những khoảng trống sinh ra do mất cache là điều không thể chấp nhận được, hoặc nếu bạn chỉ dự trù một số lượng giá trị tương đối nhỏ (số nguyên ngắn 2-byte), thì việc lưu cache các giá trị được phân bổ trước (preallocated) có thể không phải là một lựa chọn thực tế hoặc cần thiết. Dù có thể thu hồi và khôi phục các định danh bị thất thoát, nhưng việc đó có khi lại rắc rối nhiều hơn là giá trị mà nó mang lại.

Việc phân bổ trước và lưu cache sẽ không thành vấn đề nếu mô hình có thể chấp nhận cơ chế sinh định danh muộn (late identity generation). Dưới đây là cách thực hiện với Hibernate và một Oracle sequence:

```xml
<id name="id" type="long" column="product_id">
    <generator class="sequence">
        <param name="sequence">product_seq</param>
    </generator>
</id>

```

Dưới đây là ví dụ về cách tiếp cận tương tự, nhưng sử dụng cột tự tăng (auto-increment) của MySQL:

```xml
<id name="id" type="long" column="product_id">
    <generator class="native"/>
</id>

```

Cách này mang lại hiệu năng tốt và khá dễ cấu hình trong định nghĩa ánh xạ của Hibernate. Vấn đề có thể nằm ở thời điểm sinh định danh, điều sẽ được thảo luận ngay sau đây. Phần còn lại của mục này sẽ bàn về yêu cầu sinh định danh sớm (early identity generation).

## Thứ tự sinh định danh có thể mang tính quyết định (Order May Matter)

Đôi khi, thời điểm việc sinh và gán định danh diễn ra đối với một Entity có ý nghĩa vô cùng quan trọng.

Sinh và gán định danh sớm diễn ra trước khi Entity được lưu trữ bền vững (persisted). Sinh và gán định danh muộn diễn ra tại thời điểm Entity được lưu trữ bền vững.

Ở đây, một Repository hỗ trợ cơ chế sinh sớm, cung cấp giá trị Oracle sequence khả dụng tiếp theo bằng một câu truy vấn:

```java
public ProductId nextIdentity() {
    Long rawProductId =
        (Long) this.session()
            .createSQLQuery(
                "select product_seq.nextval as product_id from dual")
            .addScalar("product_id", Hibernate.LONG)
            .uniqueResult();

    return new ProductId(rawProductId);
}

```

Vì Oracle trả về các giá trị sequence mà Hibernate mặc định ánh xạ thành các thể hiện `BigDecimal`, nên chúng ta phải thông báo cho Hibernate biết rằng chúng ta muốn kết quả `product_id` được chuyển đổi sang kiểu `Long`.

Chúng ta sẽ làm gì với các cơ sở dữ liệu như MySQL vốn không hỗ trợ sequence? MySQL hỗ trợ các cột tự tăng (auto-incrementing). Thông thường, thao tác tự tăng sẽ không diễn ra cho đến khi một dòng mới được chèn vào bảng. Tuy vậy, vẫn có cách để làm cho cơ chế auto-increment của MySQL hoạt động tương tự như một sequence trong Oracle:

```sql
mysql> CREATE TABLE product_seq (nextval INT NOT NULL);
Query OK, 0 rows affected (0.14 sec)

mysql> INSERT INTO product_seq VALUES (0);
Query OK, 1 row affected (0.03 sec)

mysql> UPDATE product_seq SET nextval=LAST_INSERT_ID(nextval + 1);
Query OK, 1 row affected (0.03 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> SELECT LAST_INSERT_ID();
+------------------+
| LAST_INSERT_ID() |
+------------------+
|                1 |
+------------------+
1 row in set (0.06 sec)

```

```sql
mysql> SELECT * FROM product_seq;
+---------+
| nextval |
+---------+
|       1 |
+---------+
1 row in set (0.00 sec)

```

Chúng ta đã tạo một bảng trong cơ sở dữ liệu MySQL có tên là `product_seq`. Tiếp theo, chúng ta chèn một dòng duy nhất vào bảng, khởi tạo giá trị của cột duy nhất, `nextval`, về `0`. Hai bước đầu tiên này thiết lập bộ giả lập sequence cho Entity `Product`. Hai câu lệnh tiếp theo minh họa việc sinh ra một giá trị sequence đơn lẻ. Chúng ta cập nhật dòng duy nhất này bằng cách tăng giá trị cột `nextval` lên `1`. Câu lệnh update sử dụng hàm `LAST_INSERT_ID()` của MySQL để tăng giá trị `INT` của cột. Biểu thức tham số được thực thi trước, sau đó kết quả được gán cho cột `nextval`. Kết quả của biểu thức tham số `nextval + 1` được giữ ổn định trong hàm `LAST_INSERT_ID()`, sao cho khi câu lệnh `SELECT LAST_INSERT_ID()` tiếp theo được đánh giá, giá trị của `nextval` sinh ra từ chính lần thực thi đó sẽ được trả về trong tập kết quả. Cuối cùng, để kiểm tra, chúng ta có thể thực thi `SELECT * FROM product_seq` nhằm chứng minh rằng giá trị hiện tại của `nextval` khớp đúng với kết quả hàm trả về.

Hibernate 3.2.3 sử dụng `org.hibernate.id.enhanced.SequenceStyleGenerator` để hỗ trợ các portable sequence (sequence có tính khả chuyển), nhưng cơ chế đó chỉ hỗ trợ sinh định danh muộn (khi Entity được chèn vào CSDL). Để hỗ trợ sinh sequence sớm trong một Repository, chúng ta sẽ phải tạo một câu truy vấn Hibernate hoặc JDBC tùy biến. Dưới đây là cách triển khai lại phương thức `nextIdentity()` của `ProductRepository` cho MySQL:

```java
public ProductId nextIdentity() {
    long rawId = -1L;
    try {
        PreparedStatement ps =
            this.connection().prepareStatement(
                "update product_seq " +
                "set next_val=LAST_INSERT_ID(next_val + 1)");

        ResultSet rs = ps.executeQuery();
        try {
            rs.next();
            rawId = rs.getLong(1);
        } finally {
            try {
                rs.close();

```

```java
            } catch(Throwable t) {
                // bỏ qua (ignore)
            }
        }
    } catch (Throwable t) {
        throw new IllegalStateException(
            "Cannot generate next identity", t);
    }

    return new ProductId(rawId);
}

```

Khi sử dụng JDBC, không cần thiết phải thực thi câu truy vấn thứ hai lên cơ sở dữ liệu để lấy kết quả của hàm `LAST_INSERT_ID()`. Câu truy vấn update đã đảm đương toàn bộ. Chúng ta lấy giá trị kiểu `long` từ `ResultSet` và sử dụng nó để khởi tạo `ProductId`.

Thủ thuật cuối cùng là lấy một kết nối JDBC từ Hibernate. Việc này có thể hơi phiền toái một chút, nhưng hoàn toàn khả thi:

```java
private Connection connection() {
    SessionFactoryImplementor sfi =
        (SessionFactoryImplementor) sessionFactory;
    ConnectionProvider cp = sfi.getConnectionProvider();
    return cp.getConnection();
}

```

Nếu không có đối tượng `Connection`, chúng ta không thể thu được `ResultSet` bằng cách thực thi `PreparedStatement`. Và nếu thiếu điều đó, việc sử dụng một portable sequence là bất khả thi.

Nhờ vào các portable sequence từ Oracle, MySQL và các cơ sở dữ liệu khác, chúng ta đã có phương tiện để sinh ra các định danh nhỏ gọn hơn, đảm bảo tính duy nhất và hỗ trợ việc tạo lập trước khi chèn (pre-insert creation).

## Bounded Context khác gán định danh (Another Bounded Context Assigns Identity)

Khi một Bounded Context khác chịu trách nhiệm gán định danh, chúng ta cần tích hợp hệ thống để tìm kiếm, so khớp và gán từng định danh tương ứng. Các mô hình tích hợp trong DDD được giải thích chi tiết trong phần Context Maps (Bản đồ Ngữ cảnh) (3) và Integrating Bounded Contexts (Tích hợp các Bounded Context) (13).

Việc so khớp chính xác (exact match) luôn là điều mong muốn nhất. Người dùng cần cung cấp một hoặc nhiều thuộc tính, chẳng hạn như số tài khoản, tên người dùng, địa chỉ email hoặc các ký hiệu duy nhất khác, để xác định chính xác đối tượng mong muốn.

Thông thường, quá trình đối soát đòi hỏi việc tìm kiếm mờ (fuzzy input), dẫn tới nhiều kết quả tìm kiếm cùng sự can thiệp lựa chọn từ phía người dùng. Hình 5.2 minh họa điều này. Người dùng nhập tiêu chí tìm kiếm tương đối ('like search' / ký tự đại diện wildcard) cho Entity cần tìm. Chúng ta gọi tới API của Bounded Context bên ngoài, nơi sẽ xử lý tìm kiếm và trả về 0, 1 hoặc nhiều đối tượng có mô tả tương tự. Sau đó, người dùng sẽ chọn một kết quả cụ thể trong số các lựa chọn đó. Định danh của đối tượng được chọn sẽ được dùng làm định danh cục bộ (local identity). Một số trạng thái bổ sung (thuộc tính) từ Entity ngoại lai cũng có thể được sao chép vào Entity cục bộ.

Hình 5.2 Kết quả tìm kiếm từ việc so khớp với một hệ thống bên ngoài để tìm định danh. Giao diện người dùng cho bước lựa chọn có thể hiển thị hoặc không hiển thị định danh. Ví dụ này có hiển thị định danh.

Điều này kéo theo những hệ lụy về mặt đồng bộ hóa. Điều gì sẽ xảy ra nếu các đối tượng được tham chiếu từ bên ngoài chuyển đổi trạng thái theo cách gây ảnh hưởng tới các Entity cục bộ? Làm sao chúng ta biết được đối tượng liên quan đã thay đổi? Vấn đề này có thể được giải quyết bằng cách sử dụng Event-Driven Architecture (4) kết hợp với Domain Event (8). Bounded Context cục bộ của chúng ta sẽ đăng ký nhận các Domain Event được xuất bản bởi các hệ thống bên ngoài. Khi nhận được một thông báo phù hợp, hệ thống cục bộ sẽ chuyển đổi trạng thái của các Aggregate Entity của chính nó để phản ánh trạng thái của đối tượng trong hệ thống bên ngoài. Đôi khi, việc đồng bộ hóa phải do chính Bounded Context cục bộ khởi xướng bằng cách đẩy các thay đổi ngược trở lại hệ thống bên ngoài gốc.

Việc này hiếm khi dễ thực hiện, nhưng nó giúp hệ thống đạt được tính tự chủ (autonomous) cao hơn. Khi đã đạt được tính tự chủ, phạm vi tìm kiếm trên thực tế có thể thu hẹp vào các đối tượng cục bộ. Đây không đơn thuần là việc lưu tạm (cache) các đối tượng ngoại lai ở cục bộ, mà nó bao gồm việc diễn dịch các khái niệm ngoại lai sang các khái niệm của Bounded Context cục bộ, như đã được giải thích trong phần Context Mapping (3).

Đây là chiến lược tạo định danh phức tạp nhất. Việc duy trì Entity cục bộ không chỉ phụ thuộc vào các bước chuyển trạng thái do hành vi nghiệp vụ cục bộ gây ra, mà còn có thể phụ thuộc vào những biến động diễn ra trong một hoặc nhiều hệ thống bên ngoài. Hãy áp dụng phương pháp này một cách thận trọng và chừng mực nhất có thể.

## Khi thời điểm sinh định danh mang tính quyết định (When the Timing of Identity Generation Matters)

Việc sinh định danh có thể diễn ra sớm (early) — như một phần trong quá trình khởi tạo đối tượng, hoặc muộn (late) — như một phần trong quá trình lưu trữ đối tượng. Đôi khi việc căn thời điểm để sinh định danh sớm là tối quan trọng, nhưng đôi khi lại không. Nếu thời điểm này thực sự quan trọng, chúng ta cần hiểu rõ những yếu tố liên quan.

Hãy xét trường hợp có lẽ là đơn giản nhất: chúng ta có thể chấp nhận việc phân bổ định danh muộn khi một Entity mới được lưu trữ, tức là khi một dòng mới được chèn vào cơ sở dữ liệu. Điều này được minh họa trong biểu đồ ở Hình 5.3. Phía client chỉ cần khởi tạo một thể hiện `Product` mới và thêm nó vào `ProductRepository`. Khi thể hiện `Product` vừa mới được tạo, client chưa cần đến định danh của nó. Và điều đó cũng thật may mắn, bởi vì lúc đó định danh vẫn chưa tồn tại. Chỉ sau khi thể hiện được lưu trữ thành công, định danh mới thực sự khả dụng.

Vậy tại sao thời điểm sinh định danh lại có thể mang tính quyết định? Hãy xem xét kịch bản trong đó client đăng ký lắng nghe các Domain Event phát ra ngoài. Một Event xuất hiện ngay khi quá trình khởi tạo một `Product` mới hoàn tất. Client lưu Event đã phát đó vào một Event Store (kho lưu trữ sự kiện) (8). Về sau, những Event đã lưu này sẽ được xuất bản dưới dạng thông báo để gửi tới các subscriber nằm bên ngoài Bounded Context. Nếu áp dụng phương pháp ở Hình 5.3, Domain Event sẽ được nhận trước khi client có cơ hội thêm `Product` mới vào `ProductRepository`. Do đó, Domain Event sẽ không chứa định danh hợp lệ của `Product` mới. Để Domain Event được khởi tạo một cách chính xác, việc sinh định danh bắt buộc phải được hoàn tất từ sớm. Hình 5.4 minh họa cho cách tiếp cận đó: Client truy vấn lấy định danh tiếp theo từ `ProductRepository`, rồi truyền nó vào constructor của `Product`.

Hình 5.3 Cách đơn giản nhất để phân bổ định danh duy nhất là để kho dữ liệu tự sinh ra nó vào lần đầu tiên đối tượng được lưu trữ.

Hình 5.4 Ở đây, định danh duy nhất được truy vấn từ Repository và được gán ngay trong quá trình khởi tạo đối tượng. Sự phức tạp của việc sinh định danh được ẩn giấu đằng sau bản triển khai của Repository.

Còn một vấn đề khác có thể nảy sinh khi việc sinh định danh bị trì hoãn cho đến khi Entity được lưu trữ. Nó xuất hiện khi hai hoặc nhiều Entity mới phải được thêm vào một tập hợp `java.util.Set`, nhưng định danh của chúng vẫn chưa được gán, khiến chúng bị coi là bằng nhau giống như các đối tượng mới khác (ví dụ: giá trị định danh đều là `null`, `0`, hoặc `-1`). Nếu phương thức `equals()` của Entity so sánh dựa trên định danh, thì những đối tượng mới được thêm vào `Set` sẽ trông giống hệt như cùng một đối tượng. Kết quả là chỉ có đối tượng đầu tiên được thêm vào được giữ lại, còn tất cả các đối tượng khác sẽ bị loại trừ. Điều này gây ra một lỗi rất khó hiểu (dubious bug) mà nguyên nhân gốc rễ ban đầu rất khó phát hiện và sửa chữa.

Để tránh lỗi này, chúng ta phải thực hiện một trong hai cách: Hoặc là chúng ta thay đổi thiết kế để phân bổ và gán định danh từ sớm, hoặc là chúng ta tái cấu trúc (refactor) phương thức `equals()` để so sánh các thuộc tính khác thay vì so sánh định danh miền nghiệp vụ. Nếu chọn phương án tái cấu trúc phương thức `equals()`, nó phải được triển khai tương tự như cách xử lý đối với một Value Object. Trong trường hợp đó, phương thức `hashCode()` của đối tượng cũng phải hài hòa và nhất quán với phương thức `equals()`:

```java
public class User extends Entity {
    ...
    @Override
    public boolean equals(Object anObject) {
        boolean equalObjects = false;

        if (anObject != null && this.getClass() == anObject.getClass()) {
            User typedObject = (User) anObject;
            equalObjects =
                this.tenantId().equals(typedObject.tenantId()) &&

```

```java
                this.username().equals(typedObject.username()));
        }

        return equalObjects;
    }

    @Override
    public int hashCode() {
        int hashCode =
            + (151513 * 229)
            + this.tenantId().hashCode()
            + this.username().hashCode();

        return hashCode;
    }
    ...
}

```

Trong trường hợp môi trường đa người thuê (multitenancy), thể hiện `TenantId` cũng được xem là một phần của định danh duy nhất. Không thể có hai đối tượng `User` thuộc hai khách thuê `Tenant` khác nhau mà lại bị coi là bằng nhau.

Đi vào trọng tâm hơn, khi đối mặt với tình huống thêm vào Set (add-to-Set) này, tôi thích việc phân bổ và gán định danh sớm hơn là phương pháp so sánh bằng theo kiểu Value. Việc các Entity sở hữu các phương thức `equals()` và `hashCode()` dựa trên định danh duy nhất của đối tượng thay vì các thuộc tính khác là điều đáng mong muốn hơn nhiều.

## Định danh thay thế (Surrogate Identity)

Một số công cụ ORM (Object-Relational Mapping — ánh xạ đối tượng với cơ sở dữ liệu quan hệ), chẳng hạn như Hibernate, lại muốn xử lý định danh đối tượng theo quy tắc riêng của chúng. Hibernate ưu tiên kiểu dữ liệu gốc của cơ sở dữ liệu (chẳng hạn như một sequence dạng số) làm định danh chính cho mỗi Entity. Nếu miền nghiệp vụ lại yêu cầu một loại định danh khác, điều này sẽ tạo ra một xung đột không mong muốn đối với Hibernate. Để khắc phục, chúng ta cần sử dụng hai định danh: Một định danh được thiết kế cho domain model và tuân thủ chặt chẽ các yêu cầu của miền nghiệp vụ; định danh còn lại phục vụ riêng cho Hibernate và được gọi là một định danh thay thế (surrogate identity).

Việc tạo một surrogate identity rất đơn giản: Tạo một thuộc tính trên Entity để lưu trữ kiểu dữ liệu của định danh thay thế (thông thường một biến kiểu `long` hoặc `int` là đủ). Đồng thời tạo một cột trong bảng cơ sở dữ liệu tương ứng để lưu định danh duy nhất này, và đặt ràng buộc khóa chính (primary key constraint) lên nó. Sau đó, bổ sung phần tử `<id>` vào định nghĩa ánh xạ Hibernate của Entity. Hãy nhớ rằng, trong trường hợp này, thuộc tính đó không có chút liên quan nào tới định danh đặc thù của miền nghiệp vụ. Nó được sinh ra hoàn toàn chỉ vì lợi ích của công cụ ORM là Hibernate.

Tốt nhất là nên ẩn thuộc tính surrogate này khỏi thế giới bên ngoài. Bởi vì surrogate identity không phải là một phần của domain model, nên việc để lộ nó ra ngoài đồng nghĩa với việc làm rò rỉ chi tiết tầng lưu trữ (persistence leakage). Dù đôi khi sự rò rỉ là khó tránh khỏi, nhưng chúng ta hoàn toàn có thể thực hiện một số biện pháp để giấu kín nó khỏi tầm mắt của các lập trình viên phát triển mô hình và phía client.

Một biện pháp bảo vệ là sử dụng mẫu Layer Supertype (siêu kiểu theo tầng) [Fowler, P of EAA]:

```java
public abstract class IdentifiedDomainObject implements Serializable {
    private long id = -1;

    public IdentifiedDomainObject() {
        super();
    }

    protected long id() {
        return this.id;
    }

    protected void setId(long anId) {
        this.id = anId;
    }
}

```

Layer Supertype này chính là `IdentifiedDomainObject`, một abstract base class (lớp cơ sở trừu tượng) giúp che giấu khóa chính thay thế khỏi tầm nhìn của các client thông qua các phương thức truy xuất có phạm vi `protected`. Phía client sẽ không bao giờ phải băn khoăn liệu những phương thức đó có dành cho mình sử dụng hay không, bởi chúng không hiển thị bên ngoài Module (9) của Entity kế thừa lớp cơ sở này. Thậm chí chúng ta có thể khai báo phạm vi `private`. Hibernate hoàn toàn không gặp bất kỳ trở ngại nào khi sử dụng cơ chế phản xạ (reflection) trên phương thức hoặc trường dữ liệu ở bất kỳ mức độ hiển thị nào, từ `public` cho tới `private`. Các Layer Supertype bổ sung khác cũng có thể mang lại nhiều giá trị, chẳng hạn như hỗ trợ cơ chế khóa lạc quan (optimistic concurrency), như được đề cập trong chương Aggregates (10).

Chúng ta cần ánh xạ thuộc tính surrogate `id` vào cột cơ sở dữ liệu thông qua định nghĩa của Hibernate. Ở đây, lớp `User` có thuộc tính `id` được ánh xạ tới cột bảng cơ sở dữ liệu có tên là `id`:

```xml
<hibernate-mapping default-cascade="all">
    <class name="com.saasovation.identityaccess.domain.model.identity.User" table="tbl_user" lazy="true">
        <id name="id" type="long" column="id" unsaved-value="-1">

```

```xml
            <generator class="native"/>
        </id>
        ...
    </class>
</hibernate-mapping>

```

Dưới đây là định nghĩa bảng MySQL dùng để lưu trữ các đối tượng `User`:

```sql
CREATE TABLE `tbl_user` (
    `id` int(11) NOT NULL auto_increment,
    `enablement_enabled` tinyint(1) NOT NULL,
    `enablement_end_date` datetime,
    `enablement_start_date` datetime,
    `password` varchar(32) NOT NULL,
    `tenant_id_id` varchar(36) NOT NULL,
    `username` varchar(25) NOT NULL,
    KEY `k_tenant_id_id` (`tenant_id_id`),
    UNIQUE KEY `k_tenant_id_username` (`tenant_id_id`,`username`),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

```

Cột đầu tiên, `id`, chính là surrogate identity. Dòng định nghĩa cột cuối cùng khai báo `id` là khóa chính của bảng. Chúng ta hoàn toàn có thể phân biệt rạch ròi giữa surrogate identity và định danh của miền nghiệp vụ. Có hai cột, `tenant_id_id` và `username`, cùng cung cấp định danh duy nhất cho miền nghiệp vụ. Chúng được kết hợp lại để tạo thành một khóa duy nhất có tên là `k_tenant_id_username`.

Không cần thiết phải bắt định danh miền nghiệp vụ đóng vai trò là khóa chính của cơ sở dữ liệu. Chúng ta cho phép trường `id` thay thế đóng vai trò là khóa chính của cơ sở dữ liệu, điều này giúp Hibernate vận hành trơn tru và dễ chịu nhất.