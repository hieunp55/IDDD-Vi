Đối với toàn bộ các hạng mục tồn đọng (outstanding items) của một sản phẩm nhất định, chúng ta sẽ duyệt lặp qua từng mục và tính tổng từng xếp hạng trong thuộc tính `BusinessPriority` (Độ ưu tiên nghiệp vụ) của chúng. Các giá trị tổng thu được từ quá trình tính toán lặp này được dùng để khởi tạo một đối tượng `BusinessPriorityTotals` (Tổng các chỉ số ưu tiên nghiệp vụ) mới rồi trả về cho phía client (phía gọi dịch vụ). Bản thân quy trình tính toán của một Service (Dịch vụ miền / Domain Service) không nhất thiết phải luôn phức tạp, dù trong một số trường hợp sự phức tạp là điều bắt buộc. Trường hợp cụ thể này tình cờ lại khá đơn giản.

Hãy lưu ý từ ví dụ này rằng bạn hoàn toàn không muốn logic này nằm trong một Application Service (Dịch vụ ứng dụng). Ngay cả khi bạn coi phép tính tổng trong vòng lặp `for` là tầm thường, nó vẫn là business logic (logic nghiệp vụ). Nhưng vẫn còn một lý do khác:

```java
BusinessPriorityTotals businessPriorityTotals =
    new BusinessPriorityTotals(
        totalBenefit,
        totalPenalty,

```

```java
        totalBenefit + totalPenalty,
        totalCost,
        totalRisk);

```

Khi `BusinessPriorityTotals` được khởi tạo, thuộc tính `totalValue` của nó được tính suy biến từ tổng của `totalBenefit` và `totalPenalty`. Logic này mang tính đặc thù của miền nghiệp vụ (domain-specific) và tuyệt đối không được phép rò rỉ sang Application Layer (Tầng ứng dụng). Chúng ta có thể lập luận rằng bản thân constructor (hàm khởi tạo) của `BusinessPriorityTotals` nên tự đảm nhận việc suy biến giá trị này từ hai tham số truyền vào. Dù đó có thể là một cách cải thiện mô hình, nhưng việc làm đó cũng không thể biện minh cho việc chuyển các phép tính còn lại sang một Application Service.

Dù chúng ta không đặt logic nghiệp vụ này trong Application Service, một Application Service vẫn đóng vai trò là client gọi đến Domain Service:

```java
public class ProductService ... {
    ...
    private BusinessPriorityTotals productBusinessPriority(
            String aTenantId,
            String aProductId) {

        BusinessPriorityTotals productBusinessPriority =
            DomainRegistry
                .businessPriorityCalculator()
                .businessPriorityTotals(
                    new TenantId(aTenantId),
                    new ProductId(aProductId));

        return productBusinessPriority;
    }
}

```

Trong trường hợp này, một phương thức private trong Application Service chịu trách nhiệm yêu cầu tính tổng độ ưu tiên nghiệp vụ cho sản phẩm. Tại đây, phương thức có thể chỉ đang cung cấp một phần payload (dữ liệu truyền tải) trả về cho client của `ProductService`, chẳng hạn như giao diện người dùng (User Interface).

## Transformation Services

Những bản triển khai Domain Service mang tính kỹ thuật sâu hơn và chắc chắn thuộc về Infrastructure (Tầng hạ tầng) thường là những dịch vụ phục vụ cho việc tích hợp (integration). Vì lý do đó, tôi chuyển các ví dụ dạng này sang Chương 13: Integrating Bounded Contexts (Tích hợp các Bounded Context). Ở đó, bạn sẽ thấy các interface (giao diện) của Service, các class triển khai, cũng như các Adapter [Gamma et al.] (bộ điều hợp) và translator (bộ chuyển đổi) được các bản triển khai này sử dụng.

## Using a Mini-Layer of Domain Services

Đôi khi, bạn có thể muốn tạo một 'mini-layer' (phân tầng nhỏ) gồm các Domain Service nằm ngay phía trên các Entity (Thực thể) và Value Object (Đối tượng giá trị) còn lại trong domain model (mô hình miền). Như tôi đã chỉ ra trước đây, hướng tiếp cận này thường đẩy hệ thống vào con đường nguy hiểm của Anemic Domain Model (Mô hình miền thiếu máu - mô hình chỉ có cấu trúc dữ liệu thuần túy mà không chứa hành vi nghiệp vụ), vốn nên bị coi là một anti-pattern (phản mẫu thiết kế).

Dẫu vậy, vẫn có một số hệ thống mà việc thiết kế thêm mini-layer các Domain Service lại hợp lý hơn và sẽ không dẫn đến Anemic Domain Model. Điều này phụ thuộc vào các đặc tính của domain model, và trong trường hợp của Identity and Access Context (Ngữ cảnh Quản lý Định danh và Quyền truy cập), cách làm này trên thực tế lại tỏ ra khá hữu ích.

Nếu làm việc trong một domain như vậy và quyết định tạo ra một mini-layer Domain Service, hãy nhớ rằng chúng luôn khác biệt hoàn toàn với các Application Service nằm ở Application Layer. Hãy xử lý transaction (giao dịch) và security (bảo mật) như các mối quan tâm của tầng ứng dụng (application concerns) bên trong Application Service, chứ không phải trong Domain Service.

## Testing Services

Chúng ta muốn kiểm thử (test) các Service của mình để đảm bảo có được góc nhìn từ phía client về cách xây dựng mô hình. Chúng ta muốn các bài test tập trung vào domain phản ánh chính xác cách thức mô hình cần được sử dụng, đồng thời tại thời điểm này có thể tạm bỏ qua một vài khía cạnh chi tiết hơn về tính đúng đắn của phần mềm.

## Isn't It a Bit Late to Test?

Thông thường tôi hay giới thiệu các bài test trước phần triển khai code thực tế. Tôi cũng đã trình bày một số đoạn mã theo phong cách test-first (viết kiểm thử trước) ở phần trước khi phân tích nhu cầu cần đến một Service. Chỉ là tôi thấy việc thảo luận về phần triển khai code sớm hơn một chút trong chương này sẽ tự nhiên hơn, chỉ vậy thôi. Tuy nhiên, điều này cho thấy test-first không phải là yêu cầu bắt buộc tuyệt đối, dù không làm vậy có thể làm giảm bớt mức độ tập trung chuẩn xác vào việc mô hình hóa.

Những bài test dưới đây minh họa cách sử dụng `AuthenticationService` sao cho đúng, và trước tiên chúng ta kiểm thử với kịch bản xác thực thành công:

```java
public class AuthenticationServiceTest extends IdentityTest {

    public void testAuthenticationSuccess() throws Exception {
        User user = this.getUserFixture();

        DomainRegistry
            .userRepository()
            .add(user);

```

```java
        UserDescriptor userDescriptor =
            DomainRegistry
                .authenticationService()
                .authenticate(
                    user.tenantId(),
                    user.username(),
                    FIXTURE_PASSWORD);

        assertNotNull(userDescriptor);
        assertEquals(user.tenantId(), userDescriptor.tenantId());
        assertEquals(user.username(), userDescriptor.username());
        assertEquals(user.person().emailAddress(), userDescriptor.emailAddress());
    }
    ...

```

Ví dụ này cho thấy cách `AuthenticationService` được client thuộc Application Service sử dụng. Đây là một happy path (kịch bản lý tưởng / luồng chạy chuẩn không phát sinh lỗi), nơi client xác thực thành công người dùng bằng cách truyền vào các tham số đúng như kỳ vọng.

Lưu ý rằng Repository (Kho lưu trữ đối tượng miền) ở đây có thể là bản triển khai đầy đủ (full implementation), một biến thể lưu trên bộ nhớ (in-memory), hoặc được mock (giả lập). Việc kiểm thử với bản triển khai đầy đủ vẫn hoạt động tốt nếu tốc độ đủ nhanh, miễn là bài test kết thúc bằng thao tác rollback (quay lui giao dịch), ngăn chặn việc tích tụ các thực thể rác giữa các lần chạy test. Việc lựa chọn loại triển khai Repository nào để kiểm thử hoàn toàn phụ thuộc vào bạn.

Tiếp theo, chúng ta minh họa kịch bản xác thực thất bại:

```java
    public void testAuthenticationTenantFailure() throws Exception {
        User user = this.getUserFixture();

        DomainRegistry
            .userRepository()
            .add(user);

        TenantId bogusTenantId = DomainRegistry.tenantRepository().nextIdentity();

        UserDescriptor userDescriptor =
            DomainRegistry
                .authenticationService()
                .authenticate(
                    bogusTenantId, // không hợp lệ (bogus)
                    user.username(),
                    FIXTURE_PASSWORD);

        assertNull(userDescriptor);
    }

```

Bài test xác thực này thất bại vì chúng ta cố ý truyền vào một `TenantId` khác với `TenantId` mà `User` được tạo ra. Tiếp theo là minh họa trường hợp tên đăng nhập không hợp lệ:

```java
    public void testAuthenticationUsernameFailure() throws Exception {
        User user = this.getUserFixture();

        DomainRegistry
            .userRepository()
            .add(user);

        UserDescriptor userDescriptor =
            DomainRegistry
                .authenticationService()
                .authenticate(
                    user.tenantId(),
                    "bogususername",
                    user.password());

        assertNull(userDescriptor);
    }

```

Kịch bản kiểm thử xác thực này thất bại vì chúng ta truyền sai tên đăng nhập. Còn một kịch bản thất bại cuối cùng được minh họa trong các bài test này:

```java
    public void testAuthenticationPasswordFailure() throws Exception {
        User user = this.getUserFixture();

        DomainRegistry
            .userRepository()
            .add(user);

        UserDescriptor userDescriptor =
            DomainRegistry
                .authenticationService()
                .authenticate(
                    user.tenantId(),
                    user.username(),
                    "passw0rd");

        assertNull(userDescriptor);
    }
}

```

Bài test này cung cấp mật khẩu sai, dẫn đến việc xác thực thất bại. Trong mọi trường hợp minh họa kịch bản thất bại, `UserDescriptor` đều được trả về dưới dạng `null`. Đây là một chi tiết mà các client cần lưu ý, vì nó cho biết điều gì client nên mong đợi khi người dùng không được xác thực. Nó cũng chỉ ra rằng xác thực thất bại không phải là một lỗi ngoại lệ (exceptional error), mà chỉ là một khả năng diễn ra bình thường trong domain này. Nếu không, nếu việc xác thực thất bại bị coi là ngoại lệ, chúng ta đã bắt Service ném ra ngoại lệ `AuthenticationFailedException`.

Trên thực tế vẫn còn thiếu một vài bài test. Tôi sẽ để bạn tự viết test cho các kịch bản miền nghiệp vụ bao gồm: khi một `Tenant` (Bên thuê / Đơn vị thuê hệ thống) không còn hoạt động, và khi một `User` bị vô hiệu hóa. Sau đó, bạn có thể tạo các bài test cho `BusinessPriorityCalculator`.

## Wrap-Up

Trong chương này, chúng ta đã thảo luận về bản chất của một Domain Service—những gì nó đại diện và những gì không phải là nó—đồng thời phân tích khi nào nên sử dụng Service thay vì đặt thao tác trực tiếp trên Entity hoặc Value Object. Ngoài ra còn có:

* Bạn đã học được rằng việc nhận diện nhu cầu chính đáng dành cho một Service là điều cần thiết để tránh lạm dụng Service.
* Bạn được nhắc nhở rằng việc lạm dụng Domain Service sẽ dẫn đến Anemic Domain Model, một anti-pattern tai hại.
* Bạn đã thấy các bước cụ thể theo thực hành tiêu chuẩn khi triển khai một Service.
* Bạn đã cân nhắc những điểm cộng và điểm trừ của việc sử dụng Separated Interface (Mẫu giao diện tách rời).
* Bạn đã xem lại một quy trình tính toán mẫu từ Agile Project Management Context (Ngữ cảnh Quản lý Dự án Tinh gọn).
* Cuối cùng, bạn đã xem xét cách cung cấp các bài test mẫu mực để minh họa cách sử dụng các Service mà mô hình cung cấp.

Tiếp theo, chúng ta sẽ xem xét một trong những công cụ mô hình hóa chiến thuật (tactical modeling) mới hơn của DDD (Domain-Driven Design - Thiết kế hướng miền). Đó chính là building block pattern (mẫu khối dựng cơ bản) vô cùng mạnh mẽ mang tên Domain Event (Sự kiện miền).

## Chapter 8

## Domain Events

Lịch sử là phiên bản của những sự kiện trong quá khứ mà con người

đã quyết định đồng thuận cùng nhau.

—Napoléon Bonaparte

Hãy sử dụng Domain Event để ghi nhận lại một điều gì đó đã xảy ra trong domain. Đây là một công cụ mô hình hóa cực kỳ mạnh mẽ. Một khi đã quen với việc sử dụng Domain Event, bạn sẽ say mê nó và tự hỏi làm sao mình có thể tồn tại được từ trước đến nay nếu thiếu vắng nó. Để bắt đầu với Domain Event, tất cả những gì bạn cần làm là tìm kiếm sự đồng thuận về việc các Event của bạn thực sự là gì.

## Road Map to This Chapter

* Khám phá xem Domain Event là gì, cũng như khi nào và tại sao bạn nên cân nhắc sử dụng chúng.
* Học cách mô hình hóa các Event dưới dạng đối tượng (object), và khi nào chúng bắt buộc phải có định danh duy nhất (uniquely identified).
* Khảo sát mẫu thiết kế Publish-Subscribe [Gamma et al.] (Xuất bản - Đăng ký) dạng lightweight (nhẹ / nội bộ luồng) và cách nó phối hợp để thông báo cho các client.
* Tìm hiểu các thành phần nào sẽ phát hành (publish) Event và thành phần nào đóng vai trò đăng ký nhận (subscriber).
* Xem xét lý do vì sao bạn muốn xây dựng một Event Store (Kho lưu trữ sự kiện), cách thực hiện và cách sử dụng nó.
* Học hỏi từ dự án SaaSOvation về các cách khác nhau để phát hành Event tới các hệ thống tự trị (autonomous systems).

## The When and Why of Domain Events

Tra cứu tài liệu của [Evans], bạn sẽ không tìm thấy định nghĩa chính thức nào cho Domain Event. Mẫu thiết kế này được giới thiệu chi tiết vào khoảng thời gian sau khi cuốn sách đó được xuất bản. Để bắt đầu thảo luận về việc triển khai các Event trong Domain (Chương 2), hãy cân nhắc định nghĩa hiện đại sau:

Điều gì đó đã xảy ra mà các chuyên gia nghiệp vụ (domain experts) quan tâm.

Hãy mô hình hóa thông tin về hoạt động trong domain thành một chuỗi các sự kiện rời rạc. Đại diện cho mỗi sự kiện bằng một đối tượng miền (domain object). . . . Một sự kiện miền là một phần đầy đủ của mô hình miền, một đại diện cho điều gì đó đã xảy ra trong miền. [Evans, Ref, trang 20]

Làm thế nào để chúng ta xác định được liệu điều gì đó xảy ra trong miền có quan trọng đối với các chuyên gia nghiệp vụ hay không? Khi trao đổi với họ, chúng ta phải lắng nghe cẩn thận từng manh mối. Hãy lưu ý một vài cụm từ then chốt cần lắng nghe khi các chuyên gia nghiệp vụ nói chuyện:

* 'Khi . . .' ('When . . .')
* 'Nếu điều đó xảy ra . . .' ('If that happens . . .')
* 'Báo cho tôi nếu . . .' và 'Thông báo cho tôi nếu . . .' ('Inform me if . . .' và 'Notify me if . . .')
* 'Một sự việc diễn ra liên quan đến . . .' ('An occurrence of . . .')

Dĩ nhiên, với các cách diễn đạt 'Báo cho tôi nếu . . .' và 'Thông báo cho tôi nếu . . .', bản thân lời thông báo không tạo nên Event. Đó chỉ là một phát biểu về việc có ai đó trong domain muốn nhận được thông báo như một kết quả từ một sự việc quan trọng vừa diễn ra, và điều đó rất có thể đồng nghĩa với việc cần mô hình hóa một Event tường minh. Thêm vào đó, các chuyên gia nghiệp vụ có thể nói những câu như: 'Nếu chuyện đó xảy ra thì không quan trọng, nhưng nếu việc này xảy ra thì rất quan trọng.' (Hãy thay thế "chuyện đó" và "việc này" bằng điều gì đó có ý nghĩa thực tế trong domain của bạn). Tùy thuộc vào văn hóa tổ chức của bạn, có thể sẽ có các cụm từ kích hoạt (triggering phrases) khác.

## Cowboy Logic

AJ: 'Trong trường hợp tôi cần ngựa [chơi chữ: Trong sự kiện tôi cần ngựa], tôi chỉ việc hét lên: 'Lại đây nào, Trigger!' là nó phi tới ngay. Dĩ nhiên, việc cho nó biết tôi đang cầm một viên đường cũng chẳng hại gì.'

> 💡 **Giải thích thêm:** Tác giả sử dụng góc hài hước "Cowboy Logic" (Lô-gíc cao bồi) qua các nhân vật miền Tây để chơi chữ với các khái niệm Domain-Driven Design:
> * Cụm từ *"In the event that"* vừa mang nghĩa đời thường là "trong trường hợp / khi", vừa ám chỉ khái niệm "Event" (Sự kiện miền).
> * "Trigger" vừa là tên con ngựa nổi tiếng của chàng cao bồi huyền thoại Roy Rogers trong văn hóa Mỹ, vừa là thuật ngữ kỹ thuật chỉ hành động "kích hoạt" (trigger).
> * "Viên đường" (cube of sugar) tượng trưng cho thông tin/dữ liệu đính kèm (payload) thúc đẩy hành động phản hồi tức thì.
> Nguồn tham khảo: https://en.wikipedia.org/wiki/Trigger_(horse)
> 
> 

Có lẽ sẽ có những lúc ngôn ngữ nói của các chuyên gia không dẫn đến một lý do rõ ràng để mô hình hóa thành một Event, nhưng tình huống nghiệp vụ vẫn đòi hỏi điều đó. Các chuyên gia nghiệp vụ có thể nhận thức được hoặc không nhận thức được những yêu cầu dạng này, và chúng chỉ có thể được làm sáng tỏ thông qua các cuộc thảo luận liên nhóm (cross-team discussions). Điều này thường xảy ra khi các Event bắt buộc phải được phát quảng bá (broadcast) tới các dịch vụ bên ngoài, nơi các hệ thống trong doanh nghiệp của bạn đã được tách rời (decoupled) và các sự việc diễn ra khắp miền nghiệp vụ phải được truyền đạt qua lại giữa các Bounded Context (Chương 2). Những Event như vậy sẽ được phát hành (publish), và các bên đăng ký (subscribers) sẽ nhận được thông báo. Khi các Event này được các subscriber xử lý, chúng có thể tạo ra tầm ảnh hưởng sâu rộng tới cả các Bounded Context nội bộ lẫn từ xa.

## Domain Experts and Events

Dù các chuyên gia nghiệp vụ ban đầu có thể chưa nhận thức được sự cần thiết của mọi loại Event, họ vẫn nên hiểu lý do đằng sau chúng khi được tham gia vào các cuộc thảo luận về các Event cụ thể. Một khi đã đạt được sự đồng thuận rõ ràng, các Event mới sẽ trở thành một phần chính thức của Ubiquitous Language (Ngôn ngữ chung / Ngôn ngữ phổ quát, Chương 1).

Khi các Event được phân phối tới các bên quan tâm (dù trong hệ thống nội bộ hay hệ thống ngoại vi), chúng thường được dùng để thúc đẩy eventual consistency (tính nhất quán cuối cùng). Điều này là hoàn toàn có chủ đích và nằm trong thiết kế kiến trúc. Nó có thể loại bỏ sự cần thiết của two-phase commit (giao dịch phân tán cam kết hai pha / global transactions) và hỗ trợ tuân thủ các quy tắc của Aggregate (Cụm thực thể / Tập hợp thực thể, Chương 10). Một quy tắc của Aggregate quy định rằng chỉ một thực thể duy nhất được phép chỉnh sửa trong một giao dịch đơn lẻ, và mọi thay đổi phụ thuộc khác phải diễn ra trong các giao dịch riêng biệt. Do đó, các thực thể Aggregate khác trong Bounded Context cục bộ có thể được đồng bộ hóa nhờ cách tiếp cận này. Chúng ta cũng đưa các phụ thuộc ở xa về trạng thái nhất quán với một độ trễ nhất định (latency). Việc tách rời này giúp đem lại một tập hợp các dịch vụ phối hợp có khả năng mở rộng cao và hiệu năng tối ưu. Nó cũng cho phép chúng ta đạt được tính liên kết lỏng (loose coupling) giữa các hệ thống.

Hình 8.1 minh họa cách các Event có thể bắt nguồn, cách chúng được lưu trữ và chuyển tiếp, cũng như nơi chúng có thể được sử dụng. Các Event có thể được tiêu thụ bởi cả Bounded Context nội bộ lẫn Bounded Context ngoại vi.

Hình 8.1 Các Aggregate tạo ra các Event và phát hành chúng. Các subscriber có thể lưu trữ Event rồi chuyển tiếp chúng tới các subscriber ở xa, hoặc chỉ chuyển tiếp mà không lưu trữ. Việc chuyển tiếp tức thời đòi hỏi chuẩn XA (tiêu chuẩn giao dịch phân tán hai pha) trừ khi middleware nhắn tin chia sẻ chung kho lưu trữ dữ liệu với mô hình.

Ngoài ra, hãy nghĩ đến những thời điểm hệ thống của bạn thường phải thực hiện batch processing (xử lý theo lô). Có thể vào các khung giờ thấp điểm (thường là ban đêm), hệ thống của bạn thực hiện một số hoạt động bảo trì hàng ngày nào đó: xóa các đối tượng đã lỗi thời, tạo mới các đối tượng cần thiết để đáp ứng các tình huống nghiệp vụ mới hình thành, đồng bộ trạng thái giữa các đối tượng với nhau, và thậm chí thông báo cho một số người dùng nhất định rằng những điều quan trọng đã diễn ra. Thường thì việc thực hiện các quy trình batch như vậy đòi hỏi bạn phải chạy những câu truy vấn phức tạp nhằm xác định các tình huống nghiệp vụ cần xử lý. Các phép tính toán và thủ tục để giải quyết chúng rất tốn kém tài nguyên, đồng thời việc đồng bộ hóa tất cả các thay đổi đòi hỏi những giao dịch có quy mô lớn. Sẽ ra sao nếu những quy trình batch phiền toái đó có thể trở nên thừa thãi và bị loại bỏ?

Bây giờ, hãy nghĩ về những sự việc thực tế đã diễn ra trong suốt ngày hôm trước dẫn đến nhu cầu phải "chạy đuổi theo để bù đắp" (play catch-up) vào ban đêm. Nếu mỗi sự việc rời rạc đó đều được ghi nhận bằng một Event duy nhất, rồi phát hành tới các listener (bộ lắng nghe sự kiện) trong chính hệ thống của bạn, liệu điều đó có giúp đơn giản hóa mọi thứ không? Thực tế là có, nó sẽ loại bỏ các câu truy vấn phức tạp bởi vì bạn sẽ biết chính xác điều gì đã xảy ra và xảy ra khi nào, cung cấp đầy đủ ngữ cảnh về những gì cần phải diễn ra tiếp theo như một hệ quả tất yếu. Bạn chỉ việc thực thi khi nhận được thông báo của từng Event. Khối lượng xử lý vốn đang ngốn nhiều tài nguyên I/O và vi xử lý trong các đợt batch nặng nề sẽ được dàn trải thành từng đợt ngắn (short spurts) xuyên suốt cả ngày; nhờ đó, các tình huống nghiệp vụ của bạn sẽ đạt trạng thái hài hòa nhanh hơn rất nhiều, luôn sẵn sàng cho người dùng thực hiện các bước kế tiếp.

Liệu mọi command (lệnh thực thi) gửi tới Aggregate có nhất thiết dẫn đến một Event không? Nhận biết khi nào cần bỏ qua các diễn biến thừa thãi trong domain mà chuyên gia hoặc toàn bộ doanh nghiệp không quan tâm cũng quan trọng không kém gì việc nhận diện nhu cầu cần đến một Event. Dẫu vậy, tùy thuộc vào các khía cạnh triển khai kỹ thuật của mô hình hoặc mục tiêu của các hệ thống hợp tác, số lượng Event có thể sinh ra nhiều hơn so với những gì chuyên gia nghiệp vụ trực tiếp yêu cầu. Đó chính là trường hợp khi sử dụng Event Sourcing (Mô hình lưu trữ nguồn gốc sự kiện, Chương 4, Phụ lục A).

Tôi sẽ để dành một phần nội dung này cho Chương 13: Integrating Bounded Contexts (Tích hợp các Bounded Context), nhưng tại đây chúng ta sẽ xem xét các công cụ mô hình hóa cốt lõi.

## Modeling Events

Hãy lấy một yêu cầu từ Agile Project Management Context. Các chuyên gia nghiệp vụ đã nêu lên nhu cầu về một Event theo cách như sau (phần in nghiêng được thêm vào để nhấn mạnh):

*Cho phép mỗi hạng mục tồn đọng (backlog item) được cam kết vào một sprint (chu kỳ phát triển ngắn). Nó chỉ có thể được cam kết nếu nó đã được lên lịch phát hành (scheduled for release). Nếu nó đã được cam kết vào một sprint khác, trước hết nó phải được hủy cam kết (uncommitted). Khi hạng mục tồn đọng được cam kết, hãy thông báo cho sprint đó và các bên quan tâm khác.*

Khi mô hình hóa các Event, hãy đặt tên cho chúng và các thuộc tính của chúng theo Ubiquitous Language trong chính Bounded Context nơi chúng bắt nguồn. Nếu một Event là kết quả của việc thực thi một thao tác command (lệnh) trên một Aggregate, thì tên của nó thường được bắt nguồn từ chính command đã được thực thi đó. Command là nguyên nhân tạo ra Event, và do đó, tên của Event được diễn đạt chuẩn xác theo dạng command đó đã xảy ra trong quá khứ. Theo kịch bản ví dụ, khi chúng ta cam kết một backlog item vào một sprint, chúng ta phát hành một Event mô hình hóa tường minh điều đã diễn ra trong domain:

Thao tác command (Command operation):

Kết quả sự kiện (Event outcome):

BacklogItem#commitTo(Sprint aSprint)

BacklogItemCommitted

Tên của Event nêu rõ điều gì đã xảy ra (dùng thì quá khứ) bên trong Aggregate sau khi thao tác được yêu cầu thực thi thành công: 'The backlog item was committed' (Hạng mục tồn đọng đã được cam kết). Nhóm phát triển có thể mô hình hóa tên gọi chi tiết dài dòng hơn một chút, chẳng hạn như `BacklogItemCommittedToSprint`, và cách đó vẫn hoạt động tốt. Tuy nhiên, trong Ubiquitous Language của phương pháp Scrum, một backlog item không bao giờ được cam kết vào bất cứ thứ gì khác ngoài một sprint. Nói cách khác, các backlog item được "lên lịch phát hành" (scheduled for release) chứ không phải "cam kết cho đợt phát hành" (committed to a release). Do đó, hoàn toàn không có sự mơ hồ nào về việc Event này được phát hành do kết quả của việc sử dụng phương thức `commitTo()`. Vì vậy, tên Event như hiện tại đã là hoàn toàn đầy đủ ý nghĩa, và tên gọi gọn gàng hơn thì dễ đọc hơn. Tuy nhiên, nếu nhóm của bạn thích một cái tên chi tiết hơn trong một trường hợp cụ thể, hãy cứ thoải mái sử dụng.

Khi phát hành các Event từ các Aggregate, điều quan trọng là tên của Event phải phản ánh bản chất quá khứ của sự việc. Nó không phải đang diễn ra ở thời điểm hiện tại. Nó đã xảy ra trước đó. Tên gọi tốt nhất để lựa chọn chính là tên phản ánh được sự thật đó.

Sau khi đã tìm được tên gọi phù hợp, Event nên có những thuộc tính nào? Trước hết, chúng ta cần một timestamp (dấu thời gian) biểu thị thời điểm Event diễn ra. Trong Java, chúng ta có thể biểu diễn nó bằng kiểu `java.util.Date`:

```java
package com.saasovation.agilepm.domain.model.product;

public class BacklogItemCommitted implements DomainEvent {
    private Date occurredOn;
    ...
}

```

Interface tối thiểu `DomainEvent`, được cài đặt bởi tất cả các Event, đảm bảo hỗ trợ phương thức truy xuất `occurredOn()`. Nó áp đặt một contract (hợp đồng giao diện) cơ bản cho mọi Event:

```java
package com.saasovation.agilepm.domain.model;

import java.util.Date;

public interface DomainEvent {
    public Date occurredOn();
}

```

Ngoài thuộc tính này, nhóm phát triển sẽ xác định những thuộc tính nào khác là cần thiết để đại diện cho một sự việc có ý nghĩa về những gì đã diễn ra. Hãy cân nhắc đưa vào bất cứ thông tin nào cần thiết để tái hiện (trigger lại) Event đó. Thông thường, điều này bao gồm định danh (identity) của thực thể Aggregate nơi sự việc diễn ra, hoặc bất kỳ thực thể Aggregate nào có liên quan. Áp dụng hướng dẫn này, chúng ta có thể tạo các thuộc tính từ bất kỳ tham số nào gây ra Event, nếu qua thảo luận thấy chúng thực sự hữu ích. Cũng có khả năng một số giá trị chuyển đổi trạng thái (state transition) của Aggregate sau sự kiện sẽ rất hữu ích cho các subscriber.

Dưới đây là kết quả phân tích cho `BacklogItemCommitted`:

```java
package com.saasovation.agilepm.domain.model.product;

public class BacklogItemCommitted implements DomainEvent {
    private Date occurredOn;
    private BacklogItemId backlogItemId;
    private SprintId committedToSprintId;
    private TenantId tenantId;
    ...
}

```

Nhóm đã quyết định rằng định danh của `BacklogItem` và của `Sprint` là thiết yếu. `BacklogItem` chính là đối tượng mà Event xảy ra trên đó, và `Sprint` là đối tượng mà Event xảy ra cùng. Nhưng quyết định này còn bắt nguồn từ một lý do sâu xa hơn: yêu cầu nghiệp vụ dẫn đến sự cần thiết của Event này đã chỉ rõ rằng `Sprint` phải được thông báo khi một `BacklogItem` cụ thể được cam kết vào nó. Do đó, một subscriber nhận Event trong cùng Bounded Context cuối cùng sẽ phải thông báo cho `Sprint`, và nó chỉ có thể làm được điều đó nếu `BacklogItemCommitted` mang theo thuộc tính `SprintId`.

Ngoài ra, trong môi trường multitenancy (đa người thuê / kiến trúc đa người dùng), việc ghi nhận `TenantId` luôn là điều bắt buộc, ngay cả khi nó không được truyền vào dưới dạng tham số của command. Nó cần thiết cho cả Bounded Context nội bộ lẫn Bounded Context ngoại vi. Ở phạm vi nội bộ, nhóm phát triển sẽ cần `TenantId` để truy vấn `BacklogItem` và `Sprint` từ các Repository (Chương 12) tương ứng của chúng. Tương tự như vậy, bất kỳ hệ thống từ xa ở bên ngoài nào lắng nghe bản phát quảng bá của Event này cũng sẽ cần biết Event đó áp dụng cho `TenantId` nào.

Chúng ta mô hình hóa các thao tác hành vi (behavioral operations) do Event cung cấp như thế nào? Các thao tác này nhìn chung rất đơn giản vì một Event thường được thiết kế mang tính bất biến (immutable). Mục đích hàng đầu và quan trọng nhất của interface trong Event là truyền tải các thuộc tính phản ánh nguyên nhân gây ra nó. Hầu hết các Event sẽ có một constructor chỉ cho phép khởi tạo trạng thái đầy đủ (full state initialization), đi kèm với một tập hợp các phương thức truy xuất chỉ đọc (read accessors / getter) cho từng thuộc tính của nó.

Dựa trên nguyên tắc đó, dưới đây là những gì nhóm ProjectOvation đã thực hiện:

```java
package com.saasovation.agilepm.domain.model.product;

public class BacklogItemCommitted implements DomainEvent {
    ...
    public BacklogItemCommitted(
            TenantId aTenantId,
            BacklogItemId aBacklogItemId,
            SprintId aCommittedToSprintId) {

        super();

        this.setOccurredOn(new Date());
        this.setBacklogItemId(aBacklogItemId);
        this.setCommittedToSprintId(aCommittedToSprintId);
        this.setTenantId(aTenantId);
    }

    @Override
    public Date occurredOn() {
        return this.occurredOn;

```

## Chapter 8 DOMAIN EVENTS

```java
    }

    public BacklogItemId backlogItemId() {
        return this.backlogItemId;
    }

    public SprintId committedToSprintId() {
        return this.committedToSprintId;
    }

    public TenantId tenantId() {
        return this.tenant;
    }
    ...
}

```

Khi Event này được phát hành, một subscriber trong Bounded Context nội bộ có thể sử dụng nó để thông báo cho `Sprint` biết rằng một `BacklogItem` cụ thể vừa mới được cam kết vào nó:

```java
MessageConsumer.instance(messageSource, false)
    .receiveOnly(
        new String[] { "BacklogItemCommitted" },
        new MessageListener(Type.TEXT) {
            @Override
            public void handleMessage(
                    String aType,
                    String aMessageId,
                    Date aTimestamp,
                    String aTextMessage,
                    long aDeliveryTag,
                    boolean isRedelivery) throws Exception {

                // trước hết khử trùng lặp message dựa vào aMessageId
                ...
                // lấy tenantId, sprintId, và backlogItemId từ JSON
                ...
                Sprint sprint =
                    sprintRepository.sprintOfId(tenantId, sprintId);

                BacklogItem backlogItem =
                    backlogItemRepository.backlogItemOfId(
                        tenantId,
                        backlogItemId);

                sprint.commit(backlogItem);
            }
        });

```

Theo các yêu cầu của hệ thống, sau khi xử lý thông điệp "BacklogItemCommitted" cụ thể này, `Sprint` sẽ đạt trạng thái nhất quán với `BacklogItem` vừa mới được cam kết vào nó. Cách thức subscriber nhận được Event này sẽ được thảo luận ở phần sau của chương.

Nhóm phát triển nhận ra rằng có thể có một chút vấn đề ở đây: Giao dịch cập nhật `Sprint` được quản lý như thế nào? Chúng ta có thể để message handler (trình xử lý thông điệp) làm việc đó, nhưng dù thế nào đi nữa thì đoạn code trong handler cũng cần được tái cấu trúc (refactoring). Cách tốt nhất là ủy quyền (delegate) xử lý cho một

Application Service (Chương 14) để hài hòa với Hexagonal Architecture (Kiến trúc lục giác, Chương 4). Làm như vậy sẽ cho phép Application Service quản lý giao dịch—vốn là một mối quan tâm tự nhiên của tầng ứng dụng. Khi đó, đoạn code handler sẽ trông như thế này:

```java
MessageConsumer.instance(messageSource, false)
    .receiveOnly(
        new String[] { "BacklogItemCommitted" },
        new MessageListener(Type.TEXT) {
            @Override
            public void handleMessage(
                    String aType,
                    String aMessageId,
                    Date aTimestamp,
                    String aTextMessage,
                    long aDeliveryTag,
                    boolean isRedelivery) throws Exception {

                // lấy tenantId, sprintId, và backlogItemId từ JSON
                String tenantId = ...
                String sprintId = ...
                String backlogItemId = ...

                ApplicationServiceRegistry
                    .sprintService()
                    .commitBacklogItem(
                        tenantId,
                        sprintId,
                        backlogItemId);
            }
        });

```

Trong ví dụ này, việc de-duplication (khử trùng lặp) Event là không cần thiết vì thao tác cam kết một `BacklogItem` vào một `Sprint` là một thao tác mang tính idempotent (lũy đẳng - thực thi nhiều lần cho cùng một kết quả mà không làm sai lệch trạng thái). Nếu một `BacklogItem` cụ thể đã được cam kết vào `Sprint` rồi, thì yêu cầu cam kết lại hiện tại sẽ bị bỏ qua.

Có thể sẽ cần cung cấp thêm trạng thái và hành vi bổ sung nếu các subscriber đòi hỏi nhiều thông tin hơn là chỉ đơn thuần biết nguyên nhân gây ra Event. Điều này có thể được truyền tải thông qua trạng thái được làm giàu (enriched state - nhiều thuộc tính hơn) hoặc các thao tác suy biến ra trạng thái phong phú hơn. Nhờ đó, các subscriber tránh được việc phải truy vấn ngược lại Aggregate phát hành Event—vốn là việc khó khăn hoặc tốn kém tài nguyên một cách không cần thiết. Event enrichment (Làm giàu sự kiện) có thể phổ biến hơn khi sử dụng Event Sourcing, bởi vì một Event dùng để lưu trữ dữ liệu (persistence) có thể cần thêm trạng thái bổ sung khi được phát hành ra bên ngoài Bounded Context. Các ví dụ về Event enrichment được cung cấp trong Phụ lục A.

## Whiteboard Time

* Liệt kê các loại Event vốn đã xảy ra trong domain của bạn nhưng hiện chưa được ghi nhận lại.
* Ghi chú lại xem việc biến chúng thành một phần tường minh trong mô hình sẽ giúp cải thiện thiết kế của bạn như thế nào.

Cách dễ nhất có thể là xác định các Aggregate có sự phụ thuộc vào trạng thái của những Aggregate khác, nơi mà tính nhất quán cuối cùng (eventual consistency) là điều bắt buộc.

Để suy biến ra trạng thái phong phú hơn bằng các phương thức thao tác, hãy đảm bảo rằng mọi hành vi bổ sung của Event đều là Side-Effect Free (Không gây tác dụng phụ / hàm thuần túy), như đã thảo luận trong chương Value Objects (Chương 6), nhằm bảo vệ tính bất biến của đối tượng.

## With Aggregate Characteristics

Đôi khi các Event được thiết kế để tạo ra từ yêu cầu trực tiếp của client. Điều này được thực hiện để phản hồi lại một sự việc nào đó không phải là kết quả trực tiếp từ việc thực thi hành vi trên một thực thể Aggregate trong mô hình. Có thể một người dùng hệ thống đã khởi tạo một hành động nào đó vốn tự thân nó đã được xem là một Event. Khi điều đó xảy ra, Event có thể được mô hình hóa như một Aggregate và được lưu giữ trong Repository của riêng nó. Vì nó đại diện cho một sự việc đã diễn ra trong quá khứ, Repository của nó sẽ không cho phép hành động xóa bỏ.

Khi các Event được mô hình hóa theo cách này, cũng giống như các Aggregate, chúng trở thành một phần trong cấu trúc của mô hình. Do đó, chúng không chỉ đơn thuần là một bản ghi chép về sự việc trong quá khứ, mặc dù chúng cũng đóng vai trò đó.

Event vẫn được thiết kế mang tính bất biến, nhưng nó có thể được gán một định danh duy nhất (unique identity) được sinh tự động. Tuy nhiên, định danh này cũng có thể được tạo thành từ tập hợp một số thuộc tính của Event. Ngay cả khi định danh duy nhất có thể được xác định bằng một tập hợp thuộc tính, cách tốt nhất vẫn là gán cho nó một định danh duy nhất được sinh tự động như đã thảo luận trong chương Entities (Chương 5). Điều này sẽ cho phép Event trải qua nhiều thay đổi thiết kế theo thời gian mà không gây rủi ro cho tính độc nhất của nó so với tất cả các Event khác.

Khi một Event được mô hình hóa theo phong cách này, nó có thể được phát hành thông qua cơ sở hạ tầng nhắn tin (messaging infrastructure) cùng lúc với thời điểm nó được thêm vào Repository của mình. Phía client có thể gọi một Domain Service (Chương 7) để tạo Event, thêm nó vào Repository, rồi phát hành nó qua messaging infrastructure. Với cách tiếp cận này, cả Repository và messaging infrastructure phải được hỗ trợ bởi cùng một phiên bản lưu trữ dữ liệu (cùng data source), nếu không sẽ cần đến một global transaction (còn gọi là chuẩn XA và cam kết hai pha) để đảm bảo cả hai thao tác đều commit thành công.

Sau khi messaging infrastructure lưu thành công thông điệp Event mới vào kho dữ liệu lưu trữ (persistence store) của nó, nó sẽ gửi bất đồng bộ (asynchronously) thông điệp đó tới bất kỳ trình lắng nghe hàng đợi (queue listener), bên đăng ký kênh/sàn giao dịch (topic/exchange subscribers), hoặc actor nào nếu sử dụng Actor Model (Mô hình đồng thời dựa trên Actor). 1 Nếu messaging infrastructure sử dụng một persistence store tách biệt với kho dữ liệu mà mô hình sử dụng, đồng thời không hỗ trợ global transaction, thì Domain Service của bạn sẽ phải đảm bảo rằng Event trước tiên được lưu vào Event Store (Kho lưu trữ sự kiện)—trong trường hợp này cũng đóng vai trò như một hàng đợi cho việc phát hành ngoài luồng (out-of-band publishing). Mỗi Event trong Event Store sau đó sẽ được xử lý bởi một thành phần chuyển tiếp (forwarding component) để gửi ra ngoài thông qua messaging infrastructure. Kỹ thuật này sẽ được thảo luận chi tiết ở phần sau của chương.

## Identity

Hãy làm rõ lý do của việc gán định danh duy nhất (unique identity). Đôi khi việc phân biệt các Event với nhau có thể là cần thiết, nhưng nhu cầu đó có thể khá hiếm gặp. Trong Bounded Context nơi Event được sinh ra, tạo lập và phát hành, thường sẽ có rất ít lý do để so sánh Event này với Event khác, nếu có. Nhưng nếu vì lý do nào đó mà các Event bắt buộc phải được so sánh thì sao? Và chuyện gì sẽ xảy ra nếu một Event được thiết kế như một Aggregate?

Có thể chỉ cần để định danh của Event được đại diện bởi chính các thuộc tính của nó là đủ, tương tự như trường hợp của các Value Object. Tên/loại của Event cùng với định danh của (các) Aggregate liên quan đến nguyên nhân gây ra nó, cũng như timestamp ghi nhận thời điểm Event diễn ra, có thể đã đủ để phân biệt nó với các Event khác.

Trong những trường hợp Event được mô hình hóa như một Aggregate, hoặc trong các trường hợp khác khi các Event bắt buộc phải được so sánh nhưng các thuộc tính kết hợp của chúng không đủ để phân biệt, chúng ta có thể gán cho Event một định danh duy nhất chính thức. Tuy nhiên, vẫn còn những lý do khác để gán định danh duy nhất.

1. Xem mô hình Actor Model về xử lý đồng thời của Erlang và Scala. Đặc biệt, Akka rất đáng để cân nhắc nếu bạn sử dụng Scala hoặc Java.

Định danh duy nhất có thể cần thiết khi các Event được phát hành ra bên ngoài Bounded Context cục bộ nơi chúng diễn ra, khi mà cơ sở hạ tầng nhắn tin chuyển tiếp chúng đi. Trong một số tình huống, các thông điệp riêng lẻ có thể bị phân phối nhiều hơn một lần (delivered more than once). Điều này xảy ra nếu phía gửi thông điệp bị sự cố (crash) trước khi messaging infrastructure kịp xác nhận rằng thông điệp đã được gửi.

Bất kể nguyên nhân nào dẫn đến việc tái phân phối thông điệp (redelivery), giải pháp là làm cho các subscriber ở xa phát hiện được việc chuyển phát trùng lặp và bỏ qua các thông điệp đã nhận. Để hỗ trợ điều này, một số cơ sở hạ tầng nhắn tin cung cấp một định danh thông điệp duy nhất (unique message identity) như một phần của tiêu đề/phong bì (header/envelope) bao quanh phần thân (body) của nó, khiến mô hình không cần phải tự sinh ra một định danh nữa. Ngay cả khi hệ thống nhắn tin không tự động cung cấp định danh duy nhất cho mọi thông điệp, các publisher vẫn có thể gán định danh cho chính Event hoặc cho thông điệp đó. Trong cả hai trường hợp, các subscriber ở xa đều có thể sử dụng định danh duy nhất này để quản lý việc khử trùng lặp (de-duplication) khi thông điệp bị phân phối lặp lại.

Liệu có cần cài đặt các phương thức `equals()` và `hashCode()` không? Chúng thường chỉ cần thiết nếu Bounded Context nội bộ thực sự sử dụng đến chúng. Các Event được gửi qua messaging infrastructure đôi khi không được tái tạo lại dưới dạng các đối tượng có kiểu dữ liệu gốc (native typed objects) khi các subscriber nhận được, mà được tiêu thụ dưới dạng XML, JSON hoặc key-value map. Mặt khác, khi một Event được thiết kế như một Aggregate và được lưu vào Repository riêng, kiểu Event đó bắt buộc phải cung cấp cả hai phương thức chuẩn này.

## Publishing Events from the Domain Model

Hãy tránh để domain model bị lộ ra ngoài hay phụ thuộc vào bất kỳ loại middleware messaging infrastructure nào. Những thành phần loại đó chỉ thuộc về tầng hạ tầng (infrastructure). Và dù đôi khi domain model có thể sử dụng gián tiếp hạ tầng đó, nó không bao giờ được phép ghép nối chặt chẽ (couple) một cách tường minh với hạ tầng. Chúng ta sẽ sử dụng một cách tiếp cận hoàn toàn tránh việc sử dụng infrastructure trong domain model.

Một trong những cách đơn giản và hiệu quả nhất để phát hành Domain Event mà không bị ràng buộc (coupling) với các thành phần bên ngoài domain model là tạo ra một Observer [Gamma et al.] (mẫu thiết kế Người quan sát) dạng lightweight (nhẹ / nội bộ luồng). Về mặt tên gọi, tôi sử dụng thuật ngữ Publish-Subscribe, vốn được [Gamma et al.] thừa nhận như một tên gọi khác của cùng một mẫu thiết kế. Các ví dụ trong mẫu thiết kế đó cũng như cách tôi sử dụng đều thuộc dạng lightweight vì không hề có yếu tố mạng (network) nào can dự vào việc đăng ký và phát hành Event. Tất cả các subscriber đã đăng ký đều thực thi trong cùng không gian tiến trình (process space) với publisher và chạy trên cùng một thread (luồng xử lý). Khi một Event được phát hành, từng subscriber sẽ được thông báo một cách đồng bộ (synchronously), lần lượt từng người một. Điều này cũng ngụ ý rằng tất cả các subscriber đều đang chạy bên trong cùng một giao dịch (transaction), có thể do một Application Service—vốn là client trực tiếp của domain model—kiểm soát.

Việc xem xét riêng rẽ hai nửa của Publish-Subscribe sẽ giúp giải thích rõ hơn về chúng trong ngữ cảnh của DDD.

## Publisher

Có lẽ cách sử dụng Domain Event phổ biến nhất là khi một Aggregate tạo ra một Event rồi phát hành nó. Publisher cư trú trong một Module (Chương 9) của mô hình, nhưng nó không mô hình hóa một khía cạnh cụ thể nào của domain. Đúng hơn, nó cung cấp một dịch vụ đơn giản cho các Aggregate có nhu cầu thông báo Event cho các subscriber. Dưới đây là lớp `DomainEventPublisher`, tuân thủ theo đúng định nghĩa này. Khái quát trừu tượng về cách sử dụng `DomainEventPublisher` có thể xem ở Hình 8.2.

```java
package com.saasovation.agilepm.domain.model;

import java.util.ArrayList;
import java.util.List;

public class DomainEventPublisher {

    @SuppressWarnings("unchecked")
    private static final ThreadLocal<List> subscribers =
        new ThreadLocal<List>();

    private static final ThreadLocal<Boolean> publishing =
        new ThreadLocal<Boolean>() {
            protected Boolean initialValue() {
                return Boolean.FALSE;
            }
        };

    public static DomainEventPublisher instance() {
        return new DomainEventPublisher();
    }

    public DomainEventPublisher() {
        super();
    }

    @SuppressWarnings("unchecked")
    public <T> void publish(final T aDomainEvent) {
        if (publishing.get()) {
            return;
        }

        try {
            publishing.set(Boolean.TRUE);

            List<DomainEventSubscriber<T>> registeredSubscribers =
                subscribers.get();

```

```java
            if (registeredSubscribers != null) {
                Class<?> eventType = aDomainEvent.getClass();

                for (DomainEventSubscriber<T> subscriber : registeredSubscribers) {
                    Class<?> subscribedTo = subscriber.subscribedToEventType();

                    if (subscribedTo == eventType || subscribedTo == DomainEvent.class) {
                        subscriber.handleEvent(aDomainEvent);
                    }
                }
            }
        } finally {
            publishing.set(Boolean.FALSE);
        }
    }

    public DomainEventPublisher reset() {
        if (!publishing.get()) {
            subscribers.set(null);
        }

        return this;
    }

    @SuppressWarnings("unchecked")
    public <T> void subscribe(DomainEventSubscriber<T> aSubscriber) {
        if (publishing.get()) {
            return;
        }

        List<DomainEventSubscriber<T>> registeredSubscribers = subscribers.get();

        if (registeredSubscribers == null) {
            registeredSubscribers = new ArrayList<DomainEventSubscriber<T>>();
            subscribers.set(registeredSubscribers);
        }

        registeredSubscribers.add(aSubscriber);
    }
}

```

Vì mọi yêu cầu gửi đến từ người dùng hệ thống đều được xử lý trên một luồng (thread) chuyên dụng riêng biệt, chúng ta phân chia các subscriber theo thread. Do đó, hai biến `ThreadLocal` (biến cục bộ theo luồng), `subscribers` và `publishing`, được cấp phát riêng cho từng thread. Khi các bên quan tâm sử dụng phương thức `subscribe()` để tự đăng ký, tham chiếu đối tượng subscriber sẽ được thêm vào `List` gắn liền với luồng (thread-bound List) đó. Có thể đăng ký số lượng tùy ý các subscriber trên mỗi thread.

Tùy thuộc vào application server (máy chủ ứng dụng), các thread có thể được gom vào pool (thread pool) và tái sử dụng qua từng request. Chúng ta không muốn các subscriber đã đăng ký trên thread cho request trước đó vẫn còn tồn tại trong request tiếp theo tái sử dụng chính thread này. Khi một request mới của người dùng được hệ thống tiếp nhận, nó nên sử dụng thao tác `reset()` để xóa sạch các subscriber đã đăng ký trước đó. Điều này đảm bảo rằng các subscriber sẽ chỉ giới hạn ở những đối tượng được đăng ký kể từ thời điểm đó trở đi. Chẳng hạn, trên tầng trình diễn (presentation tier, tức 'User Interface' trong Hình 8.2), chúng ta có thể chặn (intercept) từng request bằng một filter (bộ lọc). Thành phần đánh chặn này sẽ bằng cách nào đó gọi thao tác `reset()`:

Hình 8.2 Góc nhìn trừu tượng về trình tự tương tác (sequence interactions) giữa Observer dạng lightweight, Giao diện Người dùng (User Interface, Chương 14), các Application Service, và Domain Model (Chương 1)

```java
// trong một thành phần Web filter khi nhận request của người dùng
DomainEventPublisher.instance().reset();
...
// sau đó trong một Application Service thuộc cùng request đó
DomainEventPublisher.instance().subscribe(subscriber);

```

Tiếp nối quá trình thực thi đoạn mã này—bởi hai thành phần riêng biệt, như thấy ở Hình 8.2—sẽ chỉ có đúng một subscriber được đăng ký cho luồng đó. Từ phần triển khai của phương thức `subscribe()`, bạn có thể thấy rằng các subscriber chỉ có thể được đăng ký khi publisher không trong quá trình đang phát hành Event. Điều này ngăn chặn các sự cố như ngoại lệ sửa đổi đồng thời (concurrent modification exception) trên `List`.

Vấn đề này sẽ phát sinh rõ rệt nếu các subscriber gọi ngược lại publisher để đăng ký thêm các subscriber mới nhằm phản hồi lại một Event đang được xử lý.

Tiếp theo, hãy lưu ý cách một Aggregate phát hành một Event. Tiếp tục với ví dụ xuyên suốt, khi phương thức `commitTo()` của `BacklogItem` thực thi thành công, `BacklogItemCommitted` sẽ được phát hành:

```java
public class BacklogItem extends ConcurrencySafeEntity {
    ...
    public void commitTo(Sprint aSprint) {
        ...
        DomainEventPublisher
            .instance()
            .publish(new BacklogItemCommitted(
                this.tenantId(),
                this.backlogItemId(),
                this.sprintId()));
    }
    ...
}

```

Khi `publish()` được thực thi trên `DomainEventPublisher`, nó sẽ lặp qua tất cả các subscriber đã đăng ký. Việc gọi phương thức `subscribedToEventType()` trên từng subscriber cho phép nó lọc bỏ tất cả những subscriber không đăng ký loại Event cụ thể đó. Những subscriber phản hồi `DomainEvent.class` cho truy vấn lọc này sẽ nhận được toàn bộ các Event. Tất cả các subscriber đủ điều kiện sẽ được gửi Event vừa phát hành thông qua phương thức `handleEvent()` của chúng. Sau khi tất cả các subscriber đã được lọc hoặc đã được thông báo, publisher hoàn tất quá trình phát hành.

Tương tự như `subscribe()`, `publish()` không cho phép các yêu cầu phát hành Event lồng nhau (nested requests). Biến `Boolean` gắn liền với luồng mang tên `publishing` được kiểm tra và bắt buộc phải mang giá trị `false` thì `publish()` mới được phép lặp và điều phối (dispatch) sự kiện.

Việc phát hành Event được mở rộng như thế nào để vươn tới các Bounded Context từ xa, hỗ trợ các dịch vụ tự trị (autonomous services)? Chúng ta sẽ sớm tìm hiểu điều đó, nhưng trước hết hãy xem xét kỹ hơn về các subscriber nội bộ.

## Subscribers

Những thành phần nào sẽ đăng ký subscriber để lắng nghe các Domain Event? Nhìn chung, các Application Service (Chương 14), và đôi khi là các Domain Service, sẽ làm điều đó. Subscriber có thể là bất kỳ thành phần nào đang chạy trên cùng một thread với Aggregate phát hành Event, và có khả năng thực hiện đăng ký trước khi Event được phát hành. Điều này có nghĩa là subscriber được đăng ký ngay trong luồng thực thi phương thức (method execution path) có sử dụng domain model.

## Cowboy Logic

* LB: 'Tôi muốn mua một gói đặt báo dài hạn [chơi chữ: subscription] cho tờ The Fence Post để có thể tìm thêm nhiều trò đùa quê mùa, sến súa [corny] hơn nữa mà đưa vào cuốn sách này.'

> 💡 **Giải thích thêm:** Đoạn thoại mang tính tự trào hài hước tiếp tục áp dụng lối chơi chữ:
> * Từ *"subscription"* vừa có nghĩa đời thường là việc "đặt mua báo dài hạn", vừa là thuật ngữ kỹ thuật chỉ việc "đăng ký nhận sự kiện" (subscription) trong mẫu Publish-Subscribe.
> * *"The Fence Post"* là một tuần báo thông tin nông nghiệp - chăn nuôi có thật rất phổ biến ở vùng nông thôn miền Tây nước Mỹ, đồng thời nghĩa đen là "cọc hàng rào".
> * *"Corny"* vừa mang nghĩa lóng là "quê mùa, sến súa, nhạt nhẽo", vừa gợi liên tưởng đến cây ngô/bắp (corn) của vùng đồng quê.
> Nguồn tham khảo: https://www.thefencepost.com/
> 
> 

Vì các Application Service là client trực tiếp của domain model khi sử dụng Kiến trúc lục giác (Hexagonal Architecture), chúng ở một vị trí lý tưởng để đăng ký một subscriber với publisher trước khi chúng thực thi hành vi sinh ra Event trên các Aggregate. Dưới đây là một ví dụ về một Application Service thực hiện đăng ký:

```java
public class BacklogItemApplicationService ... {

    public void commitBacklogItem(
            Tenant aTenant,
            BacklogItemId aBacklogItemId,
            SprintId aSprintId) {

        DomainEventSubscriber subscriber =
            new DomainEventSubscriber<BacklogItemCommitted>() {
                @Override
                public void handleEvent(BacklogItemCommitted aDomainEvent) {
                    // xử lý sự kiện tại đây
                    ...
                }

                @Override
                public Class<BacklogItemCommitted> subscribedToEventType() {
                    return BacklogItemCommitted.class;
                }
            };

        DomainEventPublisher.instance().subscribe(subscriber);

        BacklogItem backlogItem =
            backlogItemRepository
                .backlogItemOfId(aTenant, aBacklogItemId);

        Sprint sprint =
            sprintRepository.sprintOfId(aTenant, aSprintId);

        backlogItem.commitTo(sprint);
    }
}

```

Trong ví dụ (mang tính dàn dựng có chủ ý) này, `BacklogItemApplicationService` là một Application Service, với một phương thức dịch vụ là `commitBacklogItem()`. Phương thức này khởi tạo một thực thể của lớp ẩn danh `DomainEventSubscriber`. Điều phối viên tác vụ của Application Service sau đó sẽ đăng ký subscriber này với `DomainEventPublisher`. Cuối cùng, phương thức dịch vụ sử dụng các Repository để lấy các thực thể của `BacklogItem` và `Sprint`, rồi thực thi hành vi `commitTo()` của backlog item. Khi hoàn thành, phương thức `commitTo()` sẽ phát hành một Event có kiểu `BacklogItemCommitted`.

Những gì subscriber làm với Event không được thể hiện trong ví dụ này. Nó có thể gửi một email thông báo về việc một `BacklogItemCommitted` vừa diễn ra, nếu điều đó có ý nghĩa nghiệp vụ. Nó có thể lưu trữ Event vào một Event Store. Nó cũng có thể chuyển tiếp Event thông qua cơ sở hạ tầng nhắn tin. Thông thường trong hai trường hợp sau cùng này—lưu vào Event Store và chuyển tiếp bằng messaging infrastructure—chúng ta sẽ không tạo ra một Application Service dành riêng cho từng use case để xử lý Event theo cách này. Thay vào đó, chúng ta sẽ thiết kế một thành phần subscriber đơn nhiệm duy nhất (single subscriber component) đảm nhận việc đó. Một ví dụ về thành phần đơn trách nhiệm thực hiện việc lưu vào Event Store sẽ được trình bày trong phần 'Event Store'.

## Be Careful about What the Event Handler Does

Hãy nhớ rằng, Application Service kiểm soát transaction. Đừng sử dụng thông báo Event để chỉnh sửa một thực thể Aggregate thứ hai. Làm như vậy là vi phạm nguyên tắc vàng (rule of thumb): chỉ chỉnh sửa một thực thể Aggregate duy nhất trên mỗi giao dịch.

Một điều mà subscriber không bao giờ nên làm là lấy ra một thực thể Aggregate khác rồi thực thi hành vi command sửa đổi dữ liệu trên đó. Điều này sẽ vi phạm nguyên tắc vàng về việc chỉ chỉnh sửa một thực thể Aggregate duy nhất trong một transaction đơn lẻ, như đã được thảo luận trong chương Aggregates (Chương 10). Như [Evans] đã chỉ ra, tính nhất quán của mọi thực thể Aggregate khác ngoài thực thể được thao tác trong một giao dịch duy nhất đều phải được thực thi bằng các biện pháp bất đồng bộ (asynchronous means).

Việc chuyển tiếp Event qua một cơ sở hạ tầng nhắn tin sẽ cho phép phân phối bất đồng bộ tới các subscriber ngoài luồng (out-of-band subscribers). Mỗi subscriber bất đồng bộ đó có thể sắp xếp để chỉnh sửa một thực thể Aggregate bổ sung trong một hoặc nhiều giao dịch riêng biệt. Các thực thể Aggregate bổ sung này có thể nằm trong cùng một Bounded Context hoặc ở các Bounded Context khác. Việc phát hành Event ra bên ngoài tới số lượng tùy ý các Bounded Context thuộc các Subdomain (Phân miền nghiệp vụ, Chương 2) khác sẽ nhấn mạnh từ *Domain* trong thuật ngữ *Domain Event*. Nói cách khác, Event là một khái niệm mang tính toàn miền (domain-wide), chứ không chỉ bó hẹp trong một Bounded Context đơn lẻ. Bản hợp đồng (contract) của việc phát hành Event cần có tiềm năng mở rộng ít nhất là trên toàn bộ quy mô doanh nghiệp, hoặc thậm chí rộng hơn thế. Dẫu vậy, việc phát quảng bá rộng rãi không hề cấm việc phân phối Event cho các consumer (bên tiêu thụ) trong cùng một Bounded Context. Hãy xem lại Hình 8.1.

Đôi khi các Domain Service cũng cần phải đăng ký các subscriber. Động lực để làm điều đó cũng tương tự như lý do của Application Service, nhưng trong trường hợp này sẽ xuất phát từ các lý do mang tính đặc thù của miền nghiệp vụ (domain-specific) để lắng nghe các Event.

## Spreading the News to Remote Bounded Contexts

Có một vài cách khả thi để các Bounded Context từ xa nhận biết được các Event diễn ra trong Bounded Context của bạn. Ý tưởng cốt lõi là cần phải có một hình thức nhắn tin (messaging) nào đó diễn ra, và một cơ chế nhắn tin cấp doanh nghiệp (enterprise messaging mechanism) là điều cần thiết. Cần nói rõ rằng, cơ chế được đề cập ở đây vượt xa khỏi các thành phần Publish-Subscribe dạng lightweight, đơn giản vừa thảo luận ở trên. Tại đây, chúng ta đang bàn về thứ sẽ tiếp quản công việc tại điểm mà cơ chế lightweight dừng lại.

Có rất nhiều thành phần nhắn tin như vậy hiện có, và chúng thường được phân loại là middleware (phần mềm trung gian). Từ các sản phẩm mã nguồn mở như ActiveMQ, RabbitMQ, Akka, NServiceBus và MassTransit, cho đến các sản phẩm thương mại có bản quyền khác nhau, có vô số sự lựa chọn. Chúng ta cũng có thể tự phát triển nội bộ (home-grow) một hình thức nhắn tin dựa trên các REST resource (tài nguyên REST), trong đó các hệ thống tự trị đóng vai trò là các bên quan tâm chủ động kết nối tới hệ thống phát hành, yêu cầu lấy toàn bộ các thông báo Event mà chúng chưa từng tiêu thụ trước đó. Tất cả những giải pháp này đều nằm dưới chiếc ô chung của mẫu Publish-Subscribe [Gamma et al.], với các mức độ ưu nhược điểm khác nhau. Phần lớn sẽ phụ thuộc vào ngân sách, sở thích kỹ thuật, yêu cầu chức năng cũng như các phẩm chất phi chức năng (nonfunctional qualities) mà các nhóm liên quan hướng tới.

Việc sử dụng bất kỳ cơ chế nhắn tin nào như vậy giữa các Bounded Context đòi hỏi chúng ta phải chấp nhận cam kết với tính nhất quán cuối cùng (eventual consistency). Đó là điều không thể né tránh. Các thay đổi trong một mô hình tác động đến các thay đổi trong một hoặc nhiều mô hình khác sẽ không thể đạt trạng thái hoàn toàn nhất quán trong một khoảng thời gian nhất định trôi qua. Thêm vào đó, tùy thuộc vào lưu lượng truy cập (traffic) vào từng hệ thống riêng lẻ và tác động của chúng đối với những hệ thống khác, rất có thể toàn bộ hệ thống tổng thể sẽ không bao giờ hoàn toàn nhất quán tại bất kỳ một thời điểm tức thời nào.

## Messaging Infrastructure Consistency

Giữa tất cả những bàn luận sôi nổi về eventual consistency, bạn có thể sẽ ngạc nhiên khi biết rằng có ít nhất hai cơ chế trong một giải pháp nhắn tin bắt buộc phải luôn luôn nhất quán với nhau: kho dữ liệu lưu trữ (persistence store) được sử dụng bởi domain model, và kho dữ liệu lưu trữ làm nền tảng cho messaging infrastructure dùng để chuyển tiếp các Event do mô hình phát hành. Điều này là bắt buộc để đảm bảo rằng khi các thay đổi của mô hình được lưu bền vững (persisted), việc phân phối Event cũng được bảo đảm; đồng thời, nếu một Event được phân phối qua hệ thống nhắn tin, nó biểu thị một sự việc có thật được phản ánh chính xác bởi mô hình đã phát hành ra nó. Nếu một trong hai cơ chế này lệch nhịp (out of lockstep) với cơ chế còn lại, nó sẽ dẫn đến các trạng thái sai lệch trong một hoặc nhiều mô hình phụ thuộc lẫn nhau.

Tính nhất quán trong việc lưu trữ dữ liệu giữa mô hình và Event được hoàn thành như thế nào? Có ba cách cơ bản:
