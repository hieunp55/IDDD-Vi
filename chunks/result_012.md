Các surrogate primary key (khóa chính thay thế - khóa nhân tạo trong cơ sở dữ liệu không mang ý nghĩa nghiệp vụ) có thể được sử dụng xuyên suốt mô hình dữ liệu làm khóa ngoại (foreign keys) trong các bảng khác, đảm bảo tính toàn vẹn tham chiếu (referential integrity). Đây có thể là một yêu cầu đối với việc quản trị dữ liệu trong doanh nghiệp của bạn (chẳng hạn như phục vụ kiểm toán) hoặc để hỗ trợ các công cụ. Tính toàn vẹn tham chiếu cũng rất quan trọng đối với Hibernate khi kết nối các bảng lại với nhau để triển khai các kiểu ánh xạ đa dạng (chẳng hạn như 1:M - một-nhiều). Chúng cũng hỗ trợ các phép join (kết nối) bảng nhằm tối ưu hóa các truy vấn khi đọc các Aggregate (Cụm Tổng hợp) ra khỏi cơ sở dữ liệu.

## Identity Stability

Trong hầu hết các trường hợp, unique identity (định danh duy nhất) phải được bảo vệ khỏi sự chỉnh sửa, duy trì tính ổn định xuyên suốt vòng đời của Entity (Thực thể - đối tượng được phân biệt bằng định danh duy nhất) mà nó được gán vào.

Các biện pháp đơn giản có thể được áp dụng để ngăn chặn việc sửa đổi định danh. Chúng ta có thể ẩn các phương thức setter của định danh khỏi các client (bên gọi). Chúng ta cũng có thể tạo các guard (bộ bảo vệ - điều kiện kiểm tra tiền đề) bên trong các setter để ngăn chính Entity tự ý thay đổi trạng thái của định danh nếu nó đã tồn tại. Các guard được viết dưới dạng các assertion (xác thực khẳng định) trong các setter của Entity. Dưới đây là một ví dụ về một setter của định danh:

```java
public class User extends Entity {
    ...
    protected void setUsername(String aUsername) {
        if (this.username != null) {
            throw new IllegalStateException("The username may not be changed.");
        }
        if (aUsername == null) {
            throw new IllegalArgumentException("The username may not be set to null.");
        }
        this.username = aUsername;
    }
    ...
}
```

Trong ví dụ này, thuộc tính `username`, đóng vai trò là domain identity (định danh miền) của Entity `User`, chỉ có thể thay đổi duy nhất một lần, và chỉ từ nội bộ. Setter, phương thức `setUsername()`, cung cấp tính tự đóng gói (self-encapsulation) được ẩn giấu khỏi các client. Khi một hành vi công khai của Entity tự ủy quyền tới setter, phương thức này sẽ kiểm tra thuộc tính `username` xem nó đã mang giá trị khác null (`nonnull`) hay chưa. Nếu nó đã là nonnull, biểu thị một trạng thái invariant (bất biến nghiệp vụ - quy tắc nghiệp vụ luôn phải đúng trong suốt vòng đời của đối tượng) không thể thay đổi, ngoại lệ `IllegalStateException` sẽ được ném ra. Ngoại lệ này chỉ ra rằng `username` bắt buộc phải được duy trì như một trạng thái chỉ sửa đổi một lần (modify-once).

## Whiteboard Time

* Hãy xem xét một số Entity thực thụ từ miền nghiệp vụ hiện tại của bạn và viết tên của chúng ra.

Unique identity của chúng là gì, xét cả domain identity lẫn surrogate identity? Liệu có bất kỳ định danh nào sẽ được phục vụ tốt hơn bằng một phương thức sinh định danh khác, hoặc thời điểm gán định danh khác hay không?

* Hãy ghi chú bên cạnh mỗi Entity xem bạn có nên sử dụng một phương thức gán định danh khác — người dùng tự nhập, ứng dụng sinh ra, cơ sở dữ liệu sinh ra, hay do Bounded Context (Ngữ cảnh Ranh giới) khác cung cấp — và giải thích lý do tại sao (ngay cả khi bạn không thể thay đổi nó vào lúc này).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000188_60b97247a0414ea8a79610e0ef9079e73c93315ca2d430eeed6faab942b3cb1f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000189_817d87867f10e263a063dceed0d82b34cc4e8cedbe3ec752bc84ad64c87b4b3e.png)

* Hãy lưu ý bên cạnh mỗi Entity xem nó cần cơ chế sinh định danh sớm (early identity generation) hay có thể đáp ứng tốt với cơ chế sinh định danh muộn (late identity generation), và giải thích lý do.

Hãy xem xét tính ổn định của từng định danh, đây là một phương diện mà bạn có thể cải thiện nếu cần thiết.

Setter này không hề gây cản trở Hibernate khi framework này cần tái thiết lập (reconstitute) trạng thái đối tượng từ tầng lưu trữ dữ liệu bền vững (persistence). Vì đối tượng ban đầu được khởi tạo bằng constructor mặc định không tham số, thuộc tính `username` ban đầu mang giá trị `null`. Điều này cho phép quá trình tái khởi tạo diễn ra trơn tru, và setter sẽ cho phép việc gán giá trị một lần duy nhất do Hibernate khởi tạo được thực hiện. Cơ chế này thậm chí có thể được bỏ qua hoàn toàn nếu chúng ta chỉ định Hibernate sử dụng cơ chế truy cập trực tiếp vào trường dữ liệu (field access) cho mục đích lưu trữ và tái nạp dữ liệu (rehydration), thay vì truy cập qua các accessor/getter/setter.

Một bài kiểm thử khẳng định rằng guard chỉ-sửa-đổi-một-lần đã bảo vệ đúng đắn trạng thái định danh của `User`:

```java
public class UserTest extends IdentityTest {
    ...
    public void testUsernameImmutable() throws Exception {
        try {
            User user = this.userFixture();
            user.setUsername("testusername");
            fail("The username must be immutable after initialization.");
        } catch (IllegalStateException e) {
            // kết quả kỳ vọng, bỏ qua lỗi để tiếp tục
        }
    }
    ...
}
```

Bài kiểm thử mẫu mực này chứng minh cách thức mô hình vận hành. Khi hoàn thành thành công, nó chứng minh rằng phương thức `setUsername()` bảo vệ định danh nonnull hiện có không bị thay đổi. (Chúng ta sẽ thảo luận kỹ lưỡng hơn về các guard và các bài kiểm thử Entity trong phần xác thực - validation).

## Discovering Entities and Their Intrinsic Characteristics

Bây giờ hãy cùng xem xét một số bài học kinh nghiệm từ các nhóm phát triển của SaaSOvation . . .

Ban đầu, nhóm CollabOvation đã sa vào cái bẫy mô hình hóa thực thể - quan hệ (ER - entity-relationship modeling) quá nhiều ngay trong mã nguồn Java. Họ đặt quá nhiều sự tập trung vào cơ sở dữ liệu, các bảng, các cột, và cách chúng được phản ánh vào các đối tượng. Điều đó đã dẫn tới một Anemic Domain Model (Mô hình Miền Suy dinh dưỡng - mô hình chỉ chứa các thuộc tính và getter/setter mà không có hành vi nghiệp vụ) [Fowler, Anemic] bao gồm rất nhiều getter và setter. Đáng lẽ họ phải tư duy nhiều hơn về DDD (Domain-Driven Design - Thiết kế Hướng Miền). Đến

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000190_bfb3bdd24ad92638c7a2cc1d076cde1de438b2f031954d99268e7e34e830d46b.png)

thời điểm họ cần phải bóc tách mớ bòng bong bảo mật phức tạp ra, như đã mô tả trong Bounded Contexts (Chương 2), họ đã học được cách tập trung nhiều hơn vào việc mô hình hóa Ubiquitous Language (Ngôn ngữ Toàn diện - ngôn ngữ chung thống nhất giữa chuyên gia nghiệp vụ và đội ngũ phát triển). Điều đó đã mang lại những kết quả tích cực. Trong phần này, chúng ta sẽ thấy nhóm phát triển mới của Identity and Access Context đã hưởng lợi như thế nào từ những bài học kinh nghiệm đó.

Ubiquitous Language trong một Bounded Context được phân tách rõ ràng cung cấp cho chúng ta các khái niệm và thuật ngữ cần thiết để thiết kế mô hình miền. Ngôn ngữ không tự nhiên xuất hiện. Nó phải được bồi đắp thông qua các cuộc thảo luận kỹ lưỡng với các domain expert (chuyên gia miền) và thông qua việc khai phá các yêu cầu. Một số thuật ngữ được phát hiện sẽ là các danh từ gọi tên các sự vật, tính từ mô tả chúng, và động từ biểu thị những gì sự vật đó thực hiện. Sẽ là một sai lầm nếu nghĩ rằng các đối tượng chỉ đơn thuần chắt lọc thành một tập hợp các danh từ để đặt tên cho các class và động từ để đặt tên cho các thao tác nổi bật, và rằng chúng ta có thể nắm bắt được tri thức sâu sắc mà không cần bận tâm đến điều gì khác. Việc tự giới hạn bản thân theo cách đó có thể bóp nghẹt sự mượt mà và phong phú mà mô hình xứng đáng có được. Đầu tư nhiều thời gian vào các cuộc thảo luận và rà soát các đặc tả yêu cầu sẽ giúp phát triển một Ngôn ngữ phản ánh sự suy ngẫm, nỗ lực, đồng thuận và thỏa hiệp đáng kể. Cuối cùng, cả nhóm sẽ nói Ngôn ngữ đó bằng những câu hoàn chỉnh, và mô hình sẽ phản ánh rõ ràng Ngôn ngữ được sử dụng.

Nếu điều quan trọng là các kịch bản miền đặc biệt này phải được lưu giữ lâu dài sau các cuộc thảo luận nhóm, hãy ghi lại chúng trong một tài liệu mỏng nhẹ. Ở dạng sơ khai, Ubiquitous Language của bạn có thể mang hình thức của một bảng thuật ngữ (glossary) và một tập hợp các kịch bản sử dụng đơn giản. Dẫu vậy, sẽ lại là một sai lầm nữa nếu chỉ coi Ngôn ngữ đơn thuần là bảng thuật ngữ và các kịch bản. Sau cùng, Ngôn ngữ được mô hình hóa bởi chính mã nguồn của bạn, và việc giữ cho tài liệu luôn đồng bộ với mã nguồn có thể là điều rất khó khăn hoặc thậm chí bất khả thi.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000191_59f1248ddbb5587d5d35a6587ff9ccf952ef7b50041a0768e247a725f80fb0b5.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000192_b942e5c077731e7c32548ffa655a29c8e8e856667a43d00590b1c5afa7192236.png)

## Uncovering Entities and Properties

Hãy cùng lấy một ví dụ rất cơ bản. Trong Identity and Access Context, nhóm phát triển SaaSOvation biết rằng họ cần mô hình hóa một `User`. Đúng vậy, ví dụ mô hình hóa này không được lấy từ Core Domain (Chương 2), nhưng chúng ta sẽ chuyển sang ví dụ đó ở phần sau. Tại thời điểm này, tôi muốn loại bỏ sự phức tạp gia tăng vốn có của Core Domain và chỉ tập trung vào một Entity cơ bản hơn. Nó có đủ thách thức mô hình hóa để đóng vai trò như một công cụ giảng dạy hiệu quả.

Dưới đây là những gì nhóm đã nắm được về `User` thông qua các yêu cầu phần mềm ngắn gọn (chưa phải là use cases hay user stories), phản ánh sơ bộ các phát biểu từ Ubiquitous Language. Chúng thực sự cần được tinh chỉnh thêm:

* Người dùng tồn tại gắn liền với và chịu sự kiểm soát của một đơn vị thuê bao (tenancy).
* Người dùng của hệ thống phải được xác thực (authenticated).
* Người dùng sở hữu thông tin cá nhân, bao gồm tên và thông tin liên hệ.
* Thông tin cá nhân của người dùng có thể được thay đổi bởi chính họ hoặc bởi một người quản lý.
* Thông tin xác thực bảo mật của người dùng (mật khẩu) có thể được thay đổi.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000193_397c03340c8af5f117d89629553bb3b4442a482a3639ab7b2ef355b8247b2ddd.png)

Nhóm đã phải đọc và lắng nghe rất cẩn thận. Ngay khi họ nhìn thấy/nghe thấy các biến thể của từ "thay đổi" (change) được sử dụng, họ khá chắc chắn rằng mình đang xử lý ít nhất một Entity. Đúng là từ "thay đổi" cũng có thể mang nghĩa "thay thế Giá trị" (replace the Value) thay vì "thay đổi Thực thể" (change the Entity). Liệu có điều gì khác củng cố thêm lựa chọn của nhóm về việc sử dụng building block (khối xây dựng) nào hay không? Có đấy. Thuật ngữ then chốt ở đây là "được xác thực" (authenticated), đây là một chỉ dấu mạnh mẽ cho nhóm thấy rằng một cơ chế tìm kiếm phân giải nào đó cần phải được cung cấp. Nếu bạn có một tập hợp nhiều đối tượng, và một trong số các đối tượng đó cần phải được tìm ra từ số đông, bạn cần unique identity để phân biệt đối tượng đó với tất cả các đối tượng còn lại. Một lượt tìm kiếm sẽ cần phải giải quyết từ nhiều người dùng thuộc một tenant (khách thuê/đơn vị thuê bao) để chọn ra chính xác một người dùng duy nhất.

Nhưng còn phát biểu về việc tenancy kiểm soát người dùng thì sao? Điều đó chẳng phải ngụ ý rằng Entity thực sự ở đây là `Tenant`, chứ không phải `User` hay sao? Câu hỏi này mở ra một cuộc thảo luận về Aggregates (Chương 10), chủ đề mà chúng ta sẽ dành riêng cho chương đó. Tóm lại, câu trả lời là "vừa có vừa không". Có, có một Entity `Tenant`, và không, điều này không có nghĩa là không có Entity `User`. Cả hai đều là các Entity. Để hiểu tại sao `Tenant` và `User` lại là các Root (Gốc - Chương 10) của hai Aggregate khác nhau, hãy xem chương đó. Và đúng vậy, cả `User` và `Tenant` xét cho cùng đều là các dạng Aggregate, nhưng nhóm tạm thời tránh bàn tới những mối bận tâm đó ở giai đoạn đầu.

Cơ sở biện minh ở đây là mỗi `User` phải được định danh duy nhất, phân biệt rõ ràng với tất cả các đối tượng khác. Một `User` cũng phải hỗ trợ sự thay đổi theo thời gian, vì vậy nó rõ ràng là một Entity. Tại thời điểm này, việc chúng ta mô hình hóa thông tin cá nhân bên trong `User` như thế nào chưa phải là vấn đề trọng tâm.

Nhóm cần dành một chút sự chú ý để làm rõ ý nghĩa của yêu cầu đầu tiên:

* Người dùng tồn tại gắn liền với và chịu sự kiểm soát của một đơn vị thuê bao.

Ban đầu, nhóm có thể chỉ cần thêm một ghi chú hoặc thay đổi cách diễn đạt của phát biểu theo một cách nào đó để thể hiện rằng các tenant sở hữu người dùng, nhưng họ không thu thập và chứa đựng người dùng (they don't collect and contain them). Nhóm cần phải cẩn thận vì họ không muốn sa lầy vào các chi tiết kỹ thuật và mô hình hóa chiến thuật vụn vặt. Các phát biểu cần phải có ý nghĩa đối với toàn bộ thành viên trong nhóm. Họ đã thống nhất với phương án này:

* Các tenant cho phép đăng ký nhiều người dùng thông qua thư mời (by invitation).
* Các tenant có thể ở trạng thái hoạt động (active) hoặc bị vô hiệu hóa (deactivated).
* Người dùng của hệ thống phải được xác thực nhưng chỉ có thể được xác thực nếu tenant đang hoạt động.
* . . .

Chà, đó quả là một điều bất ngờ! Sau khi thảo luận sâu hơn, nhóm đã tháo gỡ gọn gàng những khúc mắc về mặt từ ngữ, đồng thời mang lại cho các yêu cầu nhiều ý nghĩa hơn rất nhiều. Họ nhận thấy rằng phát biểu ban đầu về việc người dùng chịu sự kiểm soát của tenancy là chưa đầy đủ. Thực tế là người dùng được đăng ký bên trong một tenancy, và chỉ thông qua thư mời mà thôi. Việc chỉ rõ rằng các tenant có thể hoạt động hoặc không hoạt động, và người dùng chỉ có thể được xác thực khi tenancy của họ đang hoạt động cũng là điều tối quan trọng. Việc viết lại hoàn toàn một yêu cầu, bổ sung thêm một yêu cầu khác, và làm rõ yêu cầu thứ ba đã hé lộ một định nghĩa chính xác hơn nhiều về những gì thực sự diễn ra.

Nỗ lực này đã xóa bỏ mọi sự suy diễn mơ hồ về việc thành phần nào quản lý vòng đời của người dùng, đồng thời làm rõ rằng bất kể thành phần nào sở hữu người dùng, một số người dùng có thể không khả dụng trong những hoàn cảnh cụ thể. Đó chính là những kịch bản quan trọng cần nắm bắt tại thời điểm đó.

Có vẻ như tại thời điểm này, họ đã có những bước khởi đầu của một bảng thuật ngữ cho Ubiquitous Language. Dẫu vậy, họ vẫn chưa có đủ thông tin để hoàn thiện toàn bộ các định nghĩa. Nhóm sẽ chờ thêm một thời gian nữa trước khi đưa các mục này vào bảng thuật ngữ.

Họ đã xác định được một cặp Entity đã biết, như được thể hiện trong Hình 5.5. Điều quan trọng tiếp theo là phải biết chúng sẽ được định danh duy nhất như thế nào, và những thuộc tính bổ sung nào có thể cần thiết để tìm thấy chúng giữa vô số các đối tượng cùng loại.

Hình 5.5 Hai Entity, Tenant và User, sau quá trình khám phá ban đầu

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000194_c521c2412ce55428f4c750c3b44361a57060bc97aa0f2bd7edc9ec5e1b6636dc.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000195_441886947d92dfac1c51795ae09ae3524ef9cfc5faee1d0487b85733757e6414.png)

Nhóm đã quyết định rằng họ sẽ sử dụng một chuỗi UUID đầy đủ để định danh duy nhất cho mỗi `Tenant`, đây là trường hợp ứng dụng tự sinh định danh. Giá trị chuỗi văn bản dài này hoàn toàn có lý do chính đáng để sử dụng, không chỉ vì tính duy nhất được đảm bảo, mà còn vì nó bổ sung thêm một mức độ bảo mật tốt cho mỗi khách hàng thuê bao. Sẽ rất khó để bất kỳ ai có thể đoán ngẫu nhiên ra một UUID để xâm nhập trái phép ở cấp độ đầu tiên vào dữ liệu độc quyền. Họ cũng nhận thấy sự cần thiết phải phân tách rạch ròi các Entity thuộc về từng `Tenant` với các Entity thuộc về tất cả các tenant khác. Một yêu cầu như thế này được đưa ra để giải quyết các vấn đề bảo mật bổ sung mà các khách hàng thuê bao — vốn là các doanh nghiệp cạnh tranh với nhau — quan ngại đối với các ứng dụng và dịch vụ được lưu trữ tập trung (hosted). Do đó, mọi Entity trong toàn bộ các hệ thống sẽ được "đánh dấu phân vùng" (striped) bằng định danh duy nhất này, và mọi truy vấn sẽ bắt buộc phải có định danh duy nhất đó để tìm thấy bất kỳ Entity nào, bất kể trường hợp nào.

Định danh tenant duy nhất không phải là một Entity. Nó là một loại Value (Đối tượng Giá trị). Câu hỏi đặt ra là: Định danh này nên có một kiểu chuyên biệt (specialized type), hay nó có thể chỉ là một `String` đơn giản?

Dường như không có nhu cầu mô hình hóa các Side-Effect-Free Functions (Hàm Không có Tác dụng phụ - Chương 6) trên định danh này. Nó chỉ là một biểu diễn chuỗi văn bản thập lục phân (hexadecimal) của một con số lớn. Nhưng định danh này sẽ được sử dụng rất rộng rãi. Nó sẽ được gán trên tất cả các Entity khác trong mọi Context. Trong trường hợp này, việc áp dụng strong typing (định kiểu mạnh) có thể mang lại lợi thế. Bằng cách định nghĩa một Value Object `TenantId`, nhóm có thể đảm bảo một cách tự tin hơn rằng tất cả các Entity thuộc sở hữu của khách hàng thuê bao đều được đánh dấu đúng định danh. Hình 5.6 minh họa cách điều này được mô hình hóa, với cả hai Entity `Tenant` và `User`.

`Tenant` phải có tên. Tên có thể là một thuộc tính `String` đơn giản vì nó không có hành vi đặc biệt nào. Tên giúp giải quyết các truy vấn tìm kiếm. Một nhân viên hỗ trợ kỹ thuật (help desk) sẽ cần tìm `Tenant` theo tên trước khi có thể cung cấp hỗ trợ. Đó là một thuộc tính cần thiết và là một "đặc tính nội tại" (intrinsic characteristic). Tên cũng có thể bị ràng buộc là duy nhất giữa tất cả các khách hàng thuê bao khác, nhưng điều đó lúc này chưa quá quan trọng.

Các thuộc tính khác có thể gắn liền với mỗi khách hàng thuê bao, chẳng hạn như hợp đồng hỗ trợ và mã PIN kích hoạt cuộc gọi, thông tin thanh toán và lập hóa đơn, và có thể là địa điểm kinh doanh cùng các đầu mối liên hệ khách hàng. Nhưng đó là các mối bận tâm về mặt nghiệp vụ kinh doanh, không thuộc phạm vi bảo mật. Việc cố gắng kéo dãn Identity and Access Context đi quá xa sẽ là một nỗ lực tự chuốc lấy thất bại.

Hình 5.6 Sau khi một Entity được khám phá và đặt tên, hãy tìm ra các thuộc tính/đặc tính giúp định danh duy nhất cho nó và cho phép nó được tìm thấy.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000196_9ddcbeb6dff8d16514ad636f16ffcfb7992fa3f8144bf5ff2cd18e9de67b5e45.png)

Hỗ trợ kỹ thuật sẽ được quản lý bởi một Context khác. Sau khi tìm thấy tenant theo tên, phần mềm có thể sử dụng `TenantId` duy nhất của nó. `TenantId` sau đó sẽ được sử dụng để truy cập vào Support Context (Ngữ cảnh Hỗ trợ), ví dụ như vậy, hoặc Billing Context (Ngữ cảnh Thanh toán), hoặc Customer Relationship Management Context (Ngữ cảnh Quản trị Quan hệ Khách hàng). Các hợp đồng hỗ trợ, địa điểm kinh doanh, và thông tin liên hệ khách hàng hầu như không có hoặc có rất ít mối liên hệ với bảo mật. Dẫu vậy, việc liên kết tên của khách hàng thuê bao với `Tenant` sẽ giúp nhân viên hỗ trợ nhanh chóng cung cấp sự trợ giúp cần thiết. Tên gọi này hoàn toàn thuộc về nơi đây.

Sau khi đã hoàn thành những gì dường như là bản chất cốt lõi của `Tenant`, nhóm đã chuyển sự chú ý sang Entity `User` trong một khoảng thời gian. Điều gì sẽ đóng vai trò là unique identity của nó? Hầu hết các hệ thống định danh đều hỗ trợ một username duy nhất. Việc username bao gồm những gì không quá quan trọng, miễn là nó duy nhất trong phạm vi tenant. (Username không nhất thiết phải duy nhất xuyên biên giới giữa các tenant khác nhau.) Việc xác định username của chính mình sẽ được trao quyền cho người dùng tự quyết định. Nếu doanh nghiệp thuê bao có các tiêu chí chính sách nhất định cho username, hoặc nếu tên sẽ được xác định bởi một tích hợp bảo mật liên kết (federated security), việc tuân thủ sẽ thuộc trách nhiệm của người dùng đăng ký. Nhóm chỉ đơn giản khai báo một thuộc tính `username` trên lớp `User`.

Một yêu cầu chỉ rõ rằng phải tồn tại một thông tin xác thực bảo mật. Nó chỉ ra rằng đây là một mật khẩu. Nhóm đã nắm bắt thuật ngữ này và khai báo một thuộc tính `password` trên lớp `User`. Họ kết luận rằng mật khẩu sẽ không bao giờ được lưu trữ dưới dạng văn bản rõ (clear text). Một ghi chú đã được đưa ra rằng mật khẩu phải được mã hóa. Vì họ sẽ cần một cách để mã hóa mỗi mật khẩu trước khi nó được liên kết với `User`, điều này dường như đòi hỏi một dạng Domain Service (Chương 7) nào đó. Nhóm đã tạo một vị trí giữ chỗ trong bảng thuật ngữ của Ubiquitous Language, nơi giờ đây đã có thể bắt đầu được khởi tạo. Bảng thuật ngữ này sẽ có giới hạn, nhưng rất hữu ích:

* Tenant: Một tổ chức thuê bao có định danh sử dụng các dịch vụ định danh và truy cập, cũng như các dịch vụ trực tuyến khác. Hỗ trợ việc đăng ký người dùng thông qua thư mời.
* User: Một chủ thể bảo mật (security principal) đã đăng ký bên trong một tenancy, hoàn chỉnh với tên cá nhân và thông tin liên hệ. `User` có một username duy nhất và một mật khẩu đã được mã hóa.
* Encryption Service: Cung cấp phương tiện để mã hóa mật khẩu và các dữ liệu khác không thể lưu trữ và sử dụng dưới dạng văn bản rõ.

Một câu hỏi vẫn còn bỏ ngỏ: Liệu mật khẩu có nên được coi là một phần của unique identity của `User` hay không? Suy cho cùng, nó được sử dụng để tìm một `User`. Nếu đúng như vậy, có lẽ chúng ta sẽ muốn kết hợp cả hai thuộc tính thành một Whole Value (Giá trị Hoàn chỉnh - mẫu thiết kế gom cụm các trường dữ liệu liên quan thành một đối tượng giá trị duy nhất), đặt tên cho nó đại loại như `SecurityPrincipal`. Điều đó sẽ làm cho khái niệm này trở nên tường minh hơn nhiều. Đó là một ý tưởng thú vị, nhưng nó đã bỏ sót một yêu cầu quan trọng: Mật khẩu có thể được thay đổi. Cũng có những thời điểm các dịch vụ sẽ cần tìm một `User` mà không được cung cấp mật khẩu. Việc này không phải để phục vụ xác thực. (Hãy xem xét kịch bản chúng ta cần kiểm tra xem một `User` có đang đảm nhận một Role bảo mật nào đó hay không. Chúng ta không thể yêu cầu mật khẩu để tìm một `User` mỗi lần chúng ta cần kiểm tra quyền truy cập). Mật khẩu không phải là định danh. Chúng ta vẫn có thể đưa cả username và password vào trong một truy vấn xác thực duy nhất.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000197_1dbd509b1d32781c660c1317bee8d199d1046582cda0610840b98b06f61c44b3.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000198_9aa0e5df966d34e4f8f392f9a6e1a4cfdfdc81530bce28a1413de74d3b51c34f.png)

Ý tưởng về việc tạo ra một Value type `SecurityPrincipal` đã đưa ra một đề xuất mô hình hóa đầy hấp dẫn. Nó đã được ghi lại để xem xét sau. Cũng có một số khái niệm khác chưa được khám phá, chẳng hạn như các thư mời đăng ký sẽ được cung cấp như thế nào, cùng các chi tiết về tên cá nhân và thông tin liên hệ. Nhóm sẽ giải quyết những điều đó trong vòng lặp phát triển nhanh tiếp theo.

## Digging for Essential Behavior

Sau khi các thuộc tính thiết yếu đã được xác định, nhóm có thể đi sâu vào tìm hiểu hành vi không thể thiếu (indispensable behavior) . . .

Sau khi nhìn lại các yêu cầu cơ bản mà nhóm được giao, giờ đây họ tìm kiếm hành vi của `Tenant` và `User`:

* Các tenant có thể ở trạng thái hoạt động hoặc bị vô hiệu hóa.

Khi chúng ta nghĩ về việc kích hoạt và vô hiệu hóa một `Tenant`, chúng ta có thể hình dung ra một biến cờ bật tắt kiểu Boolean. Dù điều đó có thể đúng, cách nó được triển khai ra sao không quan trọng ở đây. Nếu chúng ta đặt `active` vào ngăn thuộc tính của `Tenant` trong sơ đồ lớp (class diagram), liệu điều đó có nhất thiết truyền đạt cho người đọc bất kỳ thông tin hữu ích nào không? Trong `Tenant.java`, liệu việc khai báo thuộc tính sau có bộc lộ rõ ràng chủ đích hay không?

```java
public class Tenant extends Entity {
```

```java
    ...
    private boolean active;
    ...
```

Có lẽ là không hoàn toàn. Và ban đầu chúng ta chỉ muốn tập trung duy nhất vào các thuộc tính giúp cung cấp định danh và cho phép khớp nối trên các truy vấn. Chúng ta sẽ bổ sung các chi tiết hỗ trợ như vậy sau.

Nhóm có thể đã nghiêng về quyết định khai báo phương thức `setActive(boolean)`, mặc dù điều đó sẽ không thực sự giải quyết được thuật ngữ của yêu cầu. Không phải là các phương thức setter công khai không bao giờ phù hợp, nhưng chúng chỉ nên được sử dụng khi Ngôn ngữ cho phép

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000199_5b7d848709e04b47faf02d1d200684088c399f0c8f3c4069a54f889064c3ef73.png)

## DISCOVERING ENTITIES AND THEIR INTRINSIC CHARACTERISTICS

và thường chỉ khi bạn không phải sử dụng nhiều setter để đáp ứng một yêu cầu duy nhất. Việc sử dụng nhiều setter làm cho chủ đích trở nên mơ hồ. Chúng cũng làm phức tạp hóa việc công bố một Domain Event đơn lẻ, có ý nghĩa như một kết quả cho những gì thực chất phải là một command logic duy nhất.

Để bám sát Ngôn ngữ, nhóm nhận thấy rằng các chuyên gia miền nói về việc kích hoạt (activating) và vô hiệu hóa (deactivating). Để kết hợp thuật ngữ đó, thay vào đó họ gán các thao tác như `activate()` và `deactivate()`.

Đoạn mã nguồn sau đây là một Intention Revealing Interface (Giao diện Bộc lộ Chủ đích - mẫu thiết kế đặt tên phương thức phản ánh mục đích nghiệp vụ thay vì cơ chế kỹ thuật) [Evans] và tuân thủ Ubiquitous Language đang ngày càng phát triển của nhóm:

```java
public class Tenant extends Entity {
    ...
    public void activate() {
        // TODO: implement
    }

    public void deactivate() {
        // TODO: implement
    }
    ...
```

Để hiện thực hóa các ý tưởng của mình, trước tiên nhóm đã phát triển một bài kiểm thử để cảm nhận xem việc sử dụng các hành vi mới này sẽ như thế nào:

```java
public class TenantTest ... {
    public void testActivateDeactivate() throws Exception {
        Tenant tenant = this.tenantFixture();
        assertTrue(tenant.isActive());
        tenant.deactivate();
        assertFalse(tenant.isActive());
        tenant.activate();
        assertTrue(tenant.isActive());
    }
}
```

Sau bài kiểm thử này, nhóm cảm thấy tự tin vào chất lượng của interface. Việc viết bài kiểm thử đã giúp họ nhận ra rằng một phương thức khác, `isActive()`, là cần thiết. Họ đã thống nhất với ba phương thức mới này, như được thấy trong Hình 5.7. Bảng thuật ngữ của Ubiquitous Language cũng phong phú thêm:

* Kích hoạt tenant (Activate tenant): Tạo điều kiện thuận lợi cho việc kích hoạt một tenant bằng thao tác này, và trạng thái hiện tại có thể được xác nhận.
* Vô hiệu hóa tenant (Deactivate tenant): Tạo điều kiện thuận lợi cho việc vô hiệu hóa một tenant bằng thao tác này. Người dùng không thể được xác thực khi tenant bị vô hiệu hóa.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000200_ce3caa429250fe072b90930e21472713db76911bfad574c2c0c71e03b16176c0.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000201_7264c29c74a58c20ce84397a0d0e433f7b5b91813818561869e93b10b60725f9.png)

Hình 5.7 Hành vi không thể thiếu được gán cho Tenant trong vòng lặp phát triển nhanh đầu tiên. Một số hành vi bị lược bỏ do tính phức tạp nhưng có thể được thêm vào sớm.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000202_8b7e87c8903e80403d0f4280a1372182b611b57a75bffc0c2d777a17fa6ae298.png)

* Authentication Service: Điều phối việc xác thực người dùng, trước tiên đảm bảo rằng tenant sở hữu người dùng đó đang hoạt động.

Mục bảng thuật ngữ cuối cùng được thêm vào ở đây chỉ ra sự khám phá ra một Domain Service khác. Trước khi cố gắng tìm kiếm thực thể `User` trùng khớp, một thành phần nào đó trước hết phải kiểm tra `Tenant` thông qua `isActive()`. Sự thấu hiểu đó có được khi nhóm cũng cân nhắc yêu cầu này:

* Người dùng của hệ thống phải được xác thực nhưng chỉ có thể được xác thực nếu tenant đang hoạt động.

Vì việc xác thực còn nhiều điều phức tạp hơn là việc chỉ đơn thuần tìm một `User` khớp với một `username` và `password` cụ thể, một bộ điều phối ở cấp độ cao hơn là cần thiết. Domain Service thực hiện rất tốt vai trò này. Các chi tiết có thể được thêm vào sau. Hiện tại, điều quan trọng là nhóm đã nắm bắt được `AuthenticationService` theo tên gọi và thêm nó vào Ubiquitous Language. Cách tiếp cận test-first (viết kiểm thử trước) thực sự đã mang lại hiệu quả.

Nhóm cũng xem xét yêu cầu sau:

* Các tenant cho phép đăng ký nhiều người dùng thông qua thư mời.

Khi bắt đầu phân tích kỹ điều này, họ hiểu rằng nó có phần phức tạp hơn mức họ muốn xử lý trong vòng lặp phát triển nhanh đầu tiên. Dường như có một loại đối tượng `Invitation` nào đó liên quan. Nhưng yêu cầu không cung cấp cho họ đủ thông tin để hiểu rõ ràng. Hành vi quản lý các thư mời cũng chưa rõ nét. Vì vậy, nhóm đã hoãn việc mô hình hóa phần này cho đến khi họ có thể thu thập thêm ý kiến đóng góp từ các chuyên gia miền và khách hàng ban đầu. Dẫu vậy, họ đã định nghĩa phương thức `registerUser()`. Phương thức này đóng vai trò thiết yếu cho việc tạo ra các thực thể `User` (xem phần 'Construction' ở phần sau của chương).

Với điều đó, họ quay trở lại lớp `User`:

* Người dùng sở hữu thông tin cá nhân, bao gồm tên và thông tin liên hệ.
* Thông tin cá nhân của người dùng có thể được thay đổi bởi chính họ hoặc bởi một người quản lý.
* Thông tin xác thực bảo mật của người dùng (mật khẩu) có thể được thay đổi.

`User` cùng với Fundamental Identity (Định danh Cơ bản), hai mẫu bảo mật thường được kết hợp với nhau, đã được áp dụng. [^1] Từ việc sử dụng thuật ngữ "cá nhân" (personal), rõ ràng là một khái niệm mang tính cá nhân đi kèm với `User`. Nhóm đã xây dựng cấu trúc hợp thành (composition) và hành vi dựa trên các phát biểu nói trên.

`Person` được mô hình hóa thành một lớp riêng biệt để tránh đặt quá nhiều trách nhiệm lên `User`. Từ "personal" đã dẫn dắt nhóm thêm `Person` vào Ubiquitous Language:

* Person: Chứa đựng và quản lý dữ liệu cá nhân về một `User`, bao gồm tên và thông tin liên hệ.

Liệu `Person` là một Entity hay một Value Object? Ở đây một lần nữa từ "thay đổi" (change) là chìa khóa. Dường như không cần thiết phải thay thế toàn bộ đối tượng `Person` chỉ vì số điện thoại cơ quan của cá nhân đó có thể thay đổi. Nhóm đã biến nó thành một Entity, như được chỉ ra trong Hình 5.8, nắm giữ hai Value: `ContactInformation` và `Name`. Đây hiện tại là những khái niệm còn mờ nhạt và sẽ được tái cấu trúc (refactored) theo thời gian.

Việc quản lý các thay đổi đối với tên cá nhân và thông tin liên hệ của một người dùng dẫn đến một số cuộc thảo luận sâu hơn. Liệu các client có nên được cấp quyền truy cập vào đối tượng `Person` bên trong `User` hay không? Một nhà phát triển đặt câu hỏi liệu một `User` có phải luôn luôn là một con người (person) hay không. Sẽ ra sao nếu đó là một hệ thống bên ngoài? Đây chưa phải là tình huống hiện tại và có thể là suy nghĩ quá vội vàng về những yêu cầu chưa rõ trong tương lai, nhưng mối lo ngại này là có cơ sở. Nếu các client được cấp quyền truy cập vào cấu trúc của `User`, với việc điều hướng sâu vào bên trong `Person` để thực thi hành vi, điều đó có thể đòi hỏi phải tái cấu trúc client sau này.

Thay vào đó, nếu họ mô hình hóa hành vi cá nhân ngay trên `User`, làm cho nó mang tính tổng quát hơn cho một chủ thể bảo mật, họ có thể sẽ tránh được một số tác động dây chuyền (ripple effects) sau này. Sau khi họ viết một vài bài kiểm thử mẫu mực để khám phá ý niệm này, dường như đó là điều đúng đắn nên làm. Họ đã mô hình hóa `User` như được thể hiện trong Hình 5.8.

Hình 5.8 Hành vi nền tảng của User thúc đẩy thêm nhiều liên kết. Không cần quá chi tiết, nhóm đã mô hình hóa thêm một vài đối tượng cùng các thao tác.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000203_70261ed7a63e99ad08fda95e6afed7a9af39aeefc08df4d498c92538bb474c97.png)

[^1]: Xem các mẫu thiết kế đã xuất bản của tôi: http://vaughnvernon.co/.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000204_ff5ff04953f29a3c66dd5fd2b8d6e5092883124e53f36760cd3d9129a6a4539c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000205_50966df4e42821bf65119a8fb7188973a495a5bc210d30328457c6ad6bade57d.png)

Còn có những cân nhắc khác. Liệu nhóm có nên phơi bày `Person` ra ngoài hay không, hay ẩn giấu nó khỏi tất cả các client? Hiện tại họ quyết định giữ cho `Person` được hiển thị cho mục đích truy vấn thông tin. Phương thức truy cập (accessor) sau đó có thể được thiết kế lại để phục vụ một interface `Principal`, trong đó `Person` và `System` mỗi bên sẽ là một `Principal` chuyên biệt. Nhóm sẽ có thể tái cấu trúc điều này khi họ đạt được sự hiểu biết sâu sắc hơn.

Duy trì nhịp độ làm việc, nhóm nhanh chóng nhận ra Ubiquitous Language được nhấn mạnh bởi yêu cầu cuối cùng hiện đang được xem xét:

* Thông tin xác thực bảo mật của người dùng (mật khẩu) có thể được thay đổi.

`User` sở hữu hành vi `changePassword()`. Điều này phản ánh chính xác thuật ngữ được sử dụng trong các yêu cầu và làm hài lòng các chuyên gia miền. Quyền truy cập vào ngay cả mật khẩu đã được mã hóa cũng không bao giờ được cấp cho các client. Một khi mật khẩu được thiết lập trên `User`, nó không bao giờ bị phơi bày ra ngoài ranh giới của Aggregate. Bất kỳ thành phần nào tìm kiếm sự xác thực chỉ có một cách tiếp cận duy nhất, đó là sử dụng `AuthenticationService`.

Nhóm cũng quyết định rằng tất cả các hành vi có thể gây ra sự sửa đổi, khi thành công, đều phải công bố một kết quả Domain Event cụ thể. Đây cũng là chi tiết vượt quá mức nhóm muốn giải quyết ở giai đoạn đầu. Nhưng họ đã nhận ra sự cần thiết của các Event. Các Event sẽ hoàn thành ít nhất hai việc. Thứ nhất, chúng cho phép theo dõi thay đổi xuyên suốt vòng đời của tất cả các đối tượng (sẽ thảo luận sau). Thứ hai, chúng cho phép các subscriber bên ngoài đồng bộ hóa với các thay đổi, mang lại cho các hệ thống bên ngoài tiềm năng đạt được tính tự trị (autonomy).

Những chủ đề đó được thảo luận trong Events (Chương 8) và Integrating Bounded Contexts (Chương 13).

## Roles and Responsibilities

Một khía cạnh của mô hình hóa là khám phá các role (vai trò) và responsibility (trách nhiệm) của các đối tượng. Phân tích vai trò và trách nhiệm có thể áp dụng cho các đối tượng miền nói chung. Ở đây chúng ta xem xét cụ thể các vai trò và trách nhiệm của các Entity.

Chúng ta cần một ngữ cảnh nhất định cho thuật ngữ "role". Một cách sử dụng, khi thảo luận về Identity and Access Context, là `Role` đóng vai trò là một Entity và Aggregate Root giải quyết một mối bận tâm bảo mật hệ thống trên diện rộng. Các client có thể hỏi xem một người dùng có thuộc về, hoặc đảm nhận một vai trò bảo mật hay không. Điều đó hoàn toàn khác biệt với những gì tôi đang thảo luận lúc này. Những gì tôi đang thảo luận trong phần này là cách các vai trò có thể được đảm nhận bởi các đối tượng trong mô hình của bạn.

## Domain Objects Playing Multiple Roles

Trong lập trình hướng đối tượng, nhìn chung các interface xác định các vai trò của một lớp triển khai. Khi được thiết kế đúng đắn, một lớp có một vai trò cho mỗi interface mà nó hiện thực hóa. Nếu lớp không có vai trò nào được khai báo rõ ràng — nó không triển khai bất kỳ interface tường minh nào — thì theo mặc định nó mang vai trò của chính lớp đó. Nghĩa là, lớp đó có interface ngầm định chính là các phương thức công khai của nó. Lớp `User` trong các ví dụ trước không triển khai interface tường minh nào, nhưng nó đảm nhận một vai trò duy nhất, một `User`.

Chúng ta có thể làm cho một đối tượng đảm nhận cả vai trò của `User` lẫn `Person`. Không phải chúng tôi đang gợi ý điều này, nhưng hiện tại hãy giả định rằng chúng ta coi đây là một ý tưởng hay. Nếu chúng ta làm như vậy, sẽ không có lý do gì để hợp thành (aggregate) một đối tượng `Person` riêng biệt như một liên kết tham chiếu của đối tượng `User`. Thay vào đó, sẽ chỉ có một đối tượng duy nhất, một đối tượng đảm nhận hai vai trò.

Tại sao chúng ta lại có thể làm điều này? Thông thường là vì chúng ta nhận thấy cả những điểm tương đồng lẫn khác biệt ở hai hoặc nhiều đối tượng. Các đặc tính giao thoa có thể được giải quyết bằng cách hòa trộn nhiều interface trên một đối tượng duy nhất. Ví dụ, chúng ta có thể để một đối tượng vừa là một `User` vừa là một `Person`, đặt tên cho lớp triển khai là `HumanUser`:

```java
public interface User {
    ...
}

public interface Person {
    ...
}

public class HumanUser implements User, Person {
    ...
}
```

Điều này có hợp lý không? Có thể, nhưng nó cũng có thể làm phức tạp hóa mọi thứ. Nếu cả hai interface đều phức tạp, có thể sẽ rất khó để triển khai cả hai trong một đối tượng duy nhất. Ngoài ra, một `User` có thể là một hệ thống, điều này sẽ làm tăng số lượng interface cần thiết lên con số ba. Việc thiết kế một đối tượng đơn lẻ đảm nhận các vai trò của `User`, `Person`, và `System` sẽ còn khó khăn hơn nữa. Có lẽ chúng ta có thể đơn giản hóa điều này bằng cách tạo ra một `Principal` đa năng:

```java
public interface User {
    ...
}

public interface Principal {
    ...
}

public class UserPrincipal implements User, Principal {
    ...
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000206_f44974492ab6da283e5b6e049bf4048ad19970a7406e36cfad0539fe522f5295.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000207_b5e91bf490cfce394d4feca730beecbb2415df379e4b8d8c50a146dfd1f84cf9.png)

Với thiết kế này, chúng ta đang cố gắng xác định kiểu chủ thể thực tế tại thời điểm thực thi (late binding - liên kết muộn). Một chủ thể dạng con người và một chủ thể dạng hệ thống có các cách triển khai khác nhau. Các hệ thống không cần loại thông tin liên hệ giống như một con người có. Dẫu vậy, chúng ta vẫn có thể thử, bằng cách thiết kế một triển khai ủy quyền chuyển tiếp (forwarding delegation). Để làm được điều đó, chúng ta sẽ kiểm tra sự tồn tại của kiểu này hay kiểu kia tại thời điểm thực thi và ủy quyền cho đối tượng đang tồn tại:

```java
public interface User {
    ...
}

public interface Principal {
    public Name principalName();
    ...
}

public class PersonPrincipal implements Principal {
    ...
}

public class SystemPrincipal implements Principal {
    ...
}

public class UserPrincipal implements User, Principal {
    private Principal personPrincipal;
    private Principal systemPrincipal;
    ...
    public Name principalName() {
        if (personPrincipal != null) {
            return personPrincipal.principalName();
        } else if (systemPrincipal != null) {
            return systemPrincipal.principalName();
        } else {
            throw new IllegalStateException("The principal is unknown.");
        }
    }
    ...
}
```

Thiết kế này làm phát sinh nhiều vấn đề khác nhau. Thứ nhất, nó mắc phải hội chứng gọi là object schizophrenia (tâm thần phân liệt đối tượng) [^2]. Hành vi được ủy quyền bằng một kỹ thuật gọi là chuyển tiếp (forwarding) hoặc điều phối (dispatching). Cả `personPrincipal` lẫn `systemPrincipal` đều không mang định danh của Entity `UserPrincipal` — nơi mà hành vi ban đầu được thực thi trên đó. Thuật ngữ object schizophrenia mô tả tình huống trong đó các đối tượng được ủy quyền không hề biết định danh của đối tượng gốc khởi tạo ra chúng. Có sự hoang mang rối loạn bên trong các đối tượng được ủy quyền về việc thực chất chúng là ai. Không phải mọi phương thức ủy quyền trong hai lớp cụ thể đều bắt buộc phải tiếp nhận định danh của đối tượng cơ sở, nhưng một số phương thức có thể sẽ cần tới nó. Chúng ta có thể truyền vào một tham chiếu tới `UserPrincipal`. Nhưng điều đó làm phức tạp thiết kế và thực tế đòi hỏi interface `Principal` phải thay đổi. Điều đó không tốt chút nào. Như [Gamma et al.] khẳng định: "Ủy quyền chỉ là một lựa chọn thiết kế tốt khi nó mang lại sự đơn giản nhiều hơn là sự phức tạp."

[^2]: Thuật ngữ này mô tả một đối tượng có nhiều nhân cách, vốn không phải là định nghĩa y khoa của bệnh tâm thần phân liệt (schizophrenia). Vấn đề thực sự đằng sau cái tên gây nhầm lẫn này là sự hỗn loạn về định danh đối tượng (object identity confusion).

> 💡 **Giải thích thêm:** "Object schizophrenia" là một thuật ngữ trong khoa học máy tính chỉ vấn đề xuất hiện khi sử dụng kỹ thuật ủy quyền (delegation). Khi đối tượng A ủy quyền thực thi cho đối tượng B, từ khóa `this` bên trong đối tượng B sẽ trỏ về chính B thay vì đối tượng ban đầu A. Điều này khiến đối tượng B bị "mất nhận thức" về đối tượng gốc đang đại diện cho nó, gây khó khăn cho việc kiểm tra danh tính, đa hình hoặc duy trì tính toàn vẹn trạng thái.
> Nguồn tham khảo: [Wikipedia - Delegation (object-oriented programming)](https://en.wikipedia.org/wiki/Delegation_(object-oriented_programming))

Chúng ta sẽ không cố gắng giải quyết thách thức mô hình hóa này ở đây. Nó chỉ được sử dụng để minh họa những thách thức đôi khi gặp phải khi sử dụng các vai trò của đối tượng và để nhấn mạnh rằng đó là một phong cách mô hình hóa mà chúng ta cần phải hết sức thận trọng. Với các công cụ phù hợp, chẳng hạn như Qi4j [Öberg], chúng ta có thể cải thiện tình hình.

Tình hình có thể được cải thiện nếu chúng ta làm cho các interface của vai trò có độ hạt mịn hơn (finer-grained), như Udi Dahan [Dahan, Roles] khuyến nghị. Dưới đây là hai yêu cầu cho phép chúng ta tạo ra các interface có độ hạt mịn:

* Thêm các đơn hàng mới vào một khách hàng.
* Nâng cấp một khách hàng thành khách hàng ưu tiên (điều kiện để đạt được cấp độ này chưa được nêu rõ).

Lớp `Customer` triển khai hai interface vai trò có độ hạt mịn: `IAddOrdersToCustomer` và `IMakeCustomerPreferred`. Mỗi interface chỉ định nghĩa một thao tác duy nhất, như được thấy trong Hình 5.9. Chúng ta thậm chí có thể triển khai các interface khác, chẳng hạn như `IValidator`.

Như đã thảo luận trong Aggregates (Chương 10), thông thường chúng ta sẽ không gom góp một số lượng lớn đối tượng, chẳng hạn như toàn bộ các đơn hàng của nó, ngay trên một `Customer`. Vì vậy, hãy xem đây là một ví dụ tổng hợp, được sử dụng chỉ nhằm mục đích minh họa cách các vai trò của đối tượng được sử dụng ra sao.

Hình 5.9 Sử dụng quy ước đặt tên của C#.NET, Entity Customer triển khai hai vai trò đối tượng, IAddOrdersToCustomer và IMakeCustomerPreferred.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000208_d9029a33f34b68be216eff942aae8228ee830b2987dbc6a09080a62b5b53d07e.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000209_61893e1943aae9949550da58904bb25b04a328e068eb57d1ecb879fc1715f586.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000210_c92d1e7a64410d7bba0f52f3cc87a3753e3269f9469e7fb6fe374d0a52fa9513.png)

Tiền tố `I` trong tên interface là một quy ước được sử dụng rộng rãi trong lập trình .NET. Bên cạnh việc tuân theo cách tiếp cận của .NET nói chung, một số người cho rằng nó làm tăng khả năng đọc hiểu: "Tôi thêm đơn hàng vào khách hàng" (I add orders to customer) và "Tôi biến khách hàng thành khách hàng ưu đãi" (I make customer preferred). Nếu không có tiền tố `I`, các tên gọi dựa trên động từ thu được có thể kém hấp dẫn hơn: `AddOrdersToCustomer` và `MakeCustomerPreferred`. Chúng ta có thể đã quen hơn với việc đặt tên interface bằng các danh từ hoặc tính từ, và tiêu chuẩn đó chắc chắn hoàn toàn có thể được áp dụng ở đây thay thế.

Hãy xem xét một số ưu điểm mà phong cách này thúc đẩy. Vai trò của một Entity có thể thay đổi từ use case này sang use case khác. Khi một client cần thêm một thực thể `Order` mới vào một `Customer`, vai trò đó khác biệt so với khi họ muốn biến `Customer` đó thành khách hàng ưu tiên. Ngoài ra còn có một lợi thế kỹ thuật. Các use case khác nhau có thể yêu cầu các chiến lược nạp dữ liệu (fetching strategies) chuyên biệt:

```csharp
IMakeCustomerPreferred customer = session.Get<IMakeCustomerPreferred>(customerId);
customer.MakePreferred();
...
IAddOrdersToCustomer customer = session.Get<IAddOrdersToCustomer>(customerId);
customer.AddOrder(order);
```

Cơ chế lưu trữ dữ liệu bền vững sẽ truy vấn tên kiểu tham số hóa `T` của phương thức `Get<T>()`. Nó sử dụng kiểu này để tra cứu một chiến lược nạp dữ liệu liên quan đã được đăng ký với hạ tầng. Nếu interface tình cờ không có chiến lược nạp dữ liệu đặc biệt nào, chiến lược mặc định sẽ được sử dụng. Bằng cách thực thi chiến lược nạp dữ liệu, đối tượng `Customer` được xác định sẽ được tải lên theo đúng hình dạng cấu trúc cần thiết cho use case cụ thể đó.

Chúng ta có thể thấy giá trị kỹ thuật khi các role marker interface (interface đánh dấu vai trò) hỗ trợ đắc lực cho việc kích hoạt các hook (điểm neo xử lý) phía sau hậu trường. Các hành vi đặc thù khác của use case có thể được gắn liền với bất kỳ vai trò nào, chẳng hạn như xác thực (validation), cho phép thực thi một validator cụ thể khi các sửa đổi của Entity đang được lưu trữ bền vững.

Các interface có độ hạt mịn giúp lớp triển khai, chẳng hạn như `Customer`, dễ dàng tự mình triển khai hành vi hơn. Không cần phải ủy quyền việc triển khai cho các lớp riêng biệt, điều này giúp ngăn ngừa hiện tượng object schizophrenia.

Hoàn toàn công bằng khi đặt câu hỏi liệu có lợi thế mô hình hóa miền rõ rệt nào trong việc tách biệt các hành vi của `Customer` theo vai trò hay không. Hãy so sánh `Customer` trước đó với `Customer` trong Hình 5.10; liệu có cái nào tốt hơn cái kia không? Liệu có dễ dàng hơn cho

## DISCOVERING ENTITIES AND THEIR INTRINSIC CHARACTERISTICS

Hình 5.10 Ở đây Customer được mô hình hóa với các thao tác trước đây nằm trên các interface khác nhau nay được gộp chung lại vào interface duy nhất của lớp Entity.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000211_507534f56eb61d6185c92a1ac22985bc9f190f5cc0e96aec1d8c3512dbb84ba5.png)

một client vô tình gọi nhầm phương thức `AddOrder()` khi đáng lẽ nó phải gọi `MakePreferred()` hay không? Có lẽ là không. Nhưng chúng ta không nên chỉ đánh giá cách tiếp cận này dựa trên mỗi yếu tố đó.

Có lẽ cách sử dụng thực tế nhất của các interface vai trò cũng chính là cách đơn giản nhất. Chúng ta có thể tận dụng các interface để che giấu các chi tiết triển khai mà chúng ta không muốn bị rò rỉ ra ngoài mô hình tới các client. Hãy thiết kế một interface để phơi bày chính xác những gì chúng ta muốn cho phép các client sử dụng, và không gì khác ngoài điều đó. Lớp triển khai có thể phức tạp hơn rất nhiều so với interface. Nó có thể có đủ loại thuộc tính hỗ trợ với các getter và setter, cùng hành vi triển khai mà các client sẽ không bao giờ có cơ hội nhìn thấy. Ví dụ, có thể một công cụ hoặc framework bắt buộc phải tạo ra các phương thức công khai mà chúng ta không hề muốn các client sử dụng. Ngay cả như vậy, interface của mô hình miền cũng không hề bị chi phối bởi các chi tiết triển khai kỹ thuật khó chịu vốn bắt buộc phải có. Điều này mang lại một lợi thế rõ rệt cho việc mô hình hóa miền.

Cùng với bất kỳ lựa chọn thiết kế nào, hãy đảm bảo rằng Ubiquitous Language luôn nắm giữ vị thế chi phối trước mọi thiên hướng kỹ thuật. Với DDD, chính mô hình của miền nghiệp vụ mới là điều quan trọng nhất.

## Construction

Khi chúng ta khởi tạo mới một Entity, chúng ta muốn sử dụng một constructor nắm bắt đủ trạng thái để định danh đầy đủ cho nó và cho phép các client có thể tìm thấy nó. Khi sử dụng cơ chế sinh định danh sớm, một constructor được thiết kế đúng đắn sẽ nhận ít nhất là unique identity làm tham số. Nếu Entity được truy vấn bằng các phương tiện khác, chẳng hạn như bằng tên hoặc phần mô tả, chúng ta cũng sẽ đưa tất cả những thông tin đó vào làm tham số constructor.

Đôi khi một Entity duy trì một hoặc nhiều invariant. Một invariant là một trạng thái bắt buộc phải duy trì tính nhất quán về mặt giao dịch xuyên suốt vòng đời của Entity. Invariant là mối bận tâm của các Aggregate, nhưng vì Aggregate Root luôn luôn là một Entity, nên nó được đề cập ở đây. Nếu một Entity có một invariant được thỏa mãn bởi trạng thái nonnull của một đối tượng chứa bên trong, hoặc được tính toán bằng cách sử dụng một trạng thái nào đó khác, thì trạng thái đó bắt buộc phải được cung cấp thông qua một hoặc nhiều tham số constructor.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000212_f743ee2ca8f413c80933330b73ec31ead2e233216cf12af29d22873034dca8a7.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000213_2505faadf37f4651818540fcc895591951449b850c10e368c7f8580323c704b1.png)

Mỗi đối tượng `User` bắt buộc phải chứa một `tenantId`, `username`, `password`, và `person`. Nói cách khác, sau khi khởi tạo thành công, các tham chiếu tới các biến thực thể (instance variables) được khai báo này tuyệt đối không bao giờ được phép mang giá trị `null`. Constructor của `User` cùng các setter của biến thực thể của nó đảm bảo điều này:

```java
public class User extends Entity {
    ...
    protected User(
            TenantId aTenantId,
            String aUsername,
            String aPassword,
            Person aPerson) {
        this();
        this.setPassword(aPassword);
        this.setPerson(aPerson);
        this.setTenantId(aTenantId);
        this.setUsername(aUsername);
        this.initialize();
    }
    ...
    protected void setPassword(String aPassword) {
        if (aPassword == null) {
            throw new IllegalArgumentException("The password may not be set to null.");
        }
        this.password = aPassword;
    }

    protected void setPerson(Person aPerson) {
        if (aPerson == null) {
            throw new IllegalArgumentException("The person may not be set to null.");
        }
        this.person = aPerson;
    }

    protected void setTenantId(TenantId aTenantId) {
        if (aTenantId == null) {
            throw new IllegalArgumentException("The tenantId may not be set to null.");
        }
        this.tenantId = aTenantId;
    }

    protected void setUsername(String aUsername) {
        if (this.username != null) {
            throw new IllegalStateException("The username may not be changed.");
        }
        if (aUsername == null) {
            throw new IllegalArgumentException("The username may not be set to null.");
        }
```

```java
        this.username = aUsername;
    }
    ...
}
```

Thiết kế của lớp `User` thể hiện sức mạnh của tính tự đóng gói (self-encapsulation). Constructor ủy quyền việc gán biến thực thể cho chính các setter thuộc tính nội bộ của nó, vốn cung cấp cơ chế tự đóng gói cho các biến. Tính tự đóng gói cho phép mỗi setter xác định các điều kiện hợp đồng thích hợp cho việc thiết lập một phần của trạng thái. Từng setter riêng lẻ sẽ xác nhận một ràng buộc nonnull thay mặt cho Entity, từ đó thực thi hợp đồng của thực thể. Các xác nhận này được gọi là các guard (xem phần 'Validation'). Như đã chỉ ra trước đây trong phần 'Identity Stability', các kỹ thuật tự đóng gói của các phương thức setter này có thể phức tạp hơn tùy theo nhu cầu.

Hãy sử dụng một Factory (Nhà máy) cho các trường hợp khởi tạo Entity phức tạp. Điều này được đề cập chi tiết hơn trong Factories (Chương 11). Trong ví dụ trước, bạn có nhận thấy rằng constructor của `User` có phạm vi truy cập `protected` không? Entity `Tenant` đóng vai trò là một Factory cho các thực thể `User`, và chỉ các lớp trong cùng một Module (Chương 9) mới có thể nhìn thấy constructor của `User`. Bằng cách đó, không đối tượng nào khác ngoài một `Tenant` có thể tạo ra các thực thể `User`:

```java
public class Tenant extends Entity {
    ...
    public User registerUser(
            String aUsername,
            String aPassword,
            Person aPerson) {
        aPerson.setTenantId(this.tenantId());
        User user = new User(
                this.tenantId(),
                aUsername,
                aPassword,
                aPerson);
        return user;
    }
    ...
}
```

Ở đây, phương thức `registerUser()` chính là Factory. Factory này đơn giản hóa việc khởi tạo trạng thái mặc định của `User` và đảm bảo rằng `TenantId` cho cả hai Entity `User` và `Person` luôn luôn chính xác. Tất cả điều này diễn ra dưới sự kiểm soát của một phương thức Factory đáp ứng Ubiquitous Language.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000214_e04640c225b04998fe28c0649546d00bb19e7d30d7baca37230f147340c8eab3.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000215_eec8397c98458f7659b8757e212d390d543ac8b50e1b8b0bea3dcaf4e6caf0a1.png)

## Validation

Những lý do chính để sử dụng validation (xác thực tính hợp lệ) trong mô hình là để kiểm tra tính đúng đắn của bất kỳ một thuộc tính đơn lẻ nào, của bất kỳ toàn bộ một đối tượng nào, hoặc của bất kỳ một cấu trúc hợp thành nào của các đối tượng. Chúng ta xem xét ba cấp độ xác thực trong mô hình. Mặc dù có rất nhiều cách để thực hiện xác thực, bao gồm cả các framework/thư viện chuyên biệt, những cách đó không được khảo sát ở đây. Thay vào đó, các phương pháp tiếp cận đa năng sẽ được trình bày, nhưng chúng có thể dẫn dắt tới các phương pháp phức tạp hơn.

Xác thực hoàn thành những mục tiêu khác nhau. Chỉ vì tất cả các thuộc tính của một đối tượng miền đều riêng lẻ hợp lệ, điều đó không có nghĩa là đối tượng đó xét như một tổng thể là hợp lệ. Có thể sự kết hợp của hai thuộc tính đúng đắn lại làm vô hiệu hóa toàn bộ đối tượng. Chỉ vì một đối tượng đơn lẻ xét như một tổng thể là hợp lệ, điều đó không có nghĩa là một cấu trúc hợp thành của các đối tượng là hợp lệ. Có lẽ sự kết hợp của hai Entity, mà mỗi Entity đều có trạng thái hợp lệ riêng rẽ, thực tế lại làm cho cấu trúc hợp thành trở nên không hợp lệ. Do đó, chúng ta có thể cần phải sử dụng một hoặc nhiều cấp độ xác thực để giải quyết tất cả các vấn đề khả dĩ.

## Validating Attributes/Properties

Làm thế nào chúng ta có thể bảo vệ một thuộc tính đơn lẻ — xem Value Objects (Chương 6) để biết sự khác biệt giữa attribute và property — khỏi bị thiết lập thành một giá trị không hợp lệ? Như đã thảo luận ở các phần khác trong chương này và cuốn sách này, tôi thực sự khuyên bạn nên sử dụng tính tự đóng gói (self-encapsulation). Tính tự đóng gói tạo điều kiện thuận lợi cho giải pháp đầu tiên.

Để trích dẫn lời của Martin Fowler: "Tự đóng gói là việc thiết kế các lớp của bạn sao cho mọi quyền truy cập vào dữ liệu, ngay cả từ bên trong cùng một lớp, đều phải đi qua các phương thức accessor" [Fowler, Self Encap]. Việc sử dụng kỹ thuật này mang lại một số lợi thế. Nó cho phép trừu tượng hóa các biến thực thể (và các biến lớp/static) của một đối tượng. Nó cung cấp một cách để dễ dàng dẫn xuất các thuộc tính từ bất kỳ số lượng thuộc tính nào khác mà đối tượng nắm giữ. Và không kém phần quan trọng đối với cuộc thảo luận cụ thể này, nó mang lại sự hỗ trợ cho một hình thức xác thực đơn giản.

Thực ra, tôi không nhất thiết thích gọi việc sử dụng tính tự đóng gói để bảo vệ trạng thái đối tượng đúng đắn bằng cái tên validation. Cái tên đó làm một số nhà phát triển cảm thấy khó chịu, bởi vì xác thực là một mối bận tâm riêng biệt và nên là trách nhiệm của một lớp xác thực, chứ không phải của một đối tượng miền. Tôi đồng ý với quan điểm đó. Dẫu vậy, điều tôi đang nói ở đây hơi khác một chút. Những gì tôi đang thảo luận là các assertion (khẳng định) tuân theo phương pháp tiếp cận design-by-contract (thiết kế theo hợp đồng).

Theo định nghĩa, design-by-contract cho phép chúng ta chỉ định các precondition (tiền điều kiện), postcondition (hậu điều kiện), và invariant (bất biến) của các thành phần mà chúng ta thiết kế. Điều này được ủng hộ bởi Bertrand Meyer và đã được thể hiện một cách thấu đáo trong ngôn ngữ lập trình Eiffel của ông. Có một số hỗ trợ cho các ngôn ngữ Java và C# cùng một cuốn sách về chủ đề này, Design Patterns and Contracts [Jezequel et al.]. Ở đây chúng ta chỉ xem xét các precondition, bằng cách áp dụng các guard, như một hình thức xác thực:

```java
public final class EmailAddress {
    private String address;

    public EmailAddress(String anAddress) {
        super();
        this.setAddress(anAddress);
    }
    ...
    private void setAddress(String anAddress) {
        if (anAddress == null) {
            throw new IllegalArgumentException("The address may not be set to null.");
        }
        if (anAddress.length() == 0) {
            throw new IllegalArgumentException("The email address is required.");
        }
        if (anAddress.length() > 100) {
            throw new IllegalArgumentException("Email address must be 100 characters or less.");
        }
        if (!java.util.regex.Pattern.matches(
                "\\w+([-+.']\\w+)*@\\w+([-.]\\w+)*\\.\\w+([-.]\\w+)*",
                anAddress)) {
            throw new IllegalArgumentException("Email address and/or its format is invalid.");
        }
        this.address = anAddress;
    }
    ...
}
```

Có bốn precondition đối với hợp đồng phương thức của `setAddress()`. Tất cả các guard của precondition đều xác nhận một điều kiện của đối số `anAddress`:

* Tham số không được phép là null.
* Tham số không được phép là một chuỗi rỗng.
* Tham số phải có độ dài từ 100 ký tự trở xuống (nhưng không được là 0 ký tự).
* Tham số phải khớp với định dạng cơ bản của một địa chỉ email.

Nếu tất cả các precondition này đều vượt qua, thuộc tính `address` sẽ được gán bằng giá trị của `anAddress`. Nếu có một điều kiện không được thỏa mãn, một ngoại lệ `IllegalArgumentException` sẽ được ném ra.

Lớp `EmailAddress` không phải là một Entity. Nó là một Value Object. Chúng ta sử dụng nó ở đây vì một vài lý do. Thứ nhất, nó là một ví dụ điển hình về việc triển khai các mức độ khác nhau của các guard precondition, từ kiểm tra null cho đến định dạng giá trị (sẽ nói thêm về điều này tiếp theo). Thứ hai, Value này được nắm giữ bởi Entity `Person` như một trong những thuộc tính của nó, một cách gián tiếp thông qua Value `ContactInformation`. Vì vậy, thực chất, đây là một phần của một Entity theo cùng một cách mà một thuộc tính đơn giản được khai báo trên một lớp Entity cũng là một phần của nó. Chúng ta sử dụng chính xác cùng một loại guard precondition khi triển khai các setter cho các thuộc tính đơn giản. Khi một Whole Value được gán cho một thuộc tính của Entity, không có cách nào để bảo vệ khỏi việc thiết lập trạng thái bất hợp lý (insane state) trừ khi các thuộc tính nhỏ hơn bên trong Value đó được bảo vệ cẩn mật.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000216_4e626eb269613487384a36d7998a8b2f57665684634e8c201a861cb3f94f264d.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000217_8f7b5db14b31d20e9c1116591f1e71de76474299b1242e4332866d9a883d0392.png)

## Cowboy Logic

* LB: 'Tôi cứ tưởng mình có một lập luận xác đáng (valid argument) khi tranh luận với bà xã, nhưng rồi đột nhiên bà ấy ném ngay một ngoại lệ đối số không hợp lệ (illegal argument exception) vào mặt tôi.'

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000218_d6b405e58716e872f15a058ff9116bd56bac3e082c795e6b21f56c4ea495369d.png)

> 💡 **Giải thích thêm:** Đây là một câu đùa chơi chữ kinh điển trong lập trình. Từ "argument" trong tiếng Anh vừa có nghĩa là "lập luận/lý lẽ trong một cuộc tranh cãi", vừa có nghĩa là "đối số truyền vào hàm". LB tưởng mình có "valid argument" (lập luận có lý / đối số hợp lệ), nhưng bà vợ lại ném ra một "illegal argument exception" (sự phản đối quyết liệt vô lý / ngoại lệ `IllegalArgumentException` trong Java khi đối số không thỏa mãn điều kiện).
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)